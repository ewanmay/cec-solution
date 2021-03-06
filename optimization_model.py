import numpy as np
import pandas as pd
import const


class OptimizationModel():

  def __init__(self, emissionTax, nonEmissiveIncentive, penaltyValues, plantProductionRates):
    self._emissionTax = emissionTax
    self._nonEmissiveIncentive = nonEmissiveIncentive
    self._plantProductionRates = plantProductionRates
    self._penaltyValues = penaltyValues
    self._sorted_penalties = self._get_sorted_penalties()
    self._cheapest_external_penalties = self._get_cheapest_external_penalties()

  
  def _get_sorted_penalties(self):
    """Get list of transport penalties from cheapest to most expensive  

    Returns:
        [list<tuple(penalty, fromZone, toZone)>]
    """
    penalties = []
    for fromZoneName in const.ZONES:
      for toZoneIdx, toZoneName in enumerate(const.ZONES):
        tup = (self._penaltyValues[fromZoneName].iloc[toZoneIdx], fromZoneName, toZoneName)
        penalties.append(tup)
    return sorted(penalties, key=lambda tup: tup[0])

  
  def _get_cheapest_external_penalties(self):
    """Get dict of cheapest out-of-province zone to send to 

    Returns:
        [dict<fromZoneName, toZoneIdx]
    """
    cheapest_external_penalties = {}    
    for fromZoneName in const.ZONES:
      cheapest_penalty = float('inf')
      cheapest_zone = -1
      for toZoneIdx in const.EXTERNAL_ZONE_INDICES:
        penalty = self._penaltyValues[fromZoneName].iloc[toZoneIdx]
        if penalty < cheapest_penalty:
            cheapest_penalty = penalty
            cheapest_zone = toZoneIdx

      cheapest_external_penalties[fromZoneName] = cheapest_zone
    return cheapest_external_penalties

  def optimize(self, predicted_data):
    """ Compute optimized power usages per month

    Args: 
      [pd.DataFrame] predicted energy consumptions in each zone for each month

    Returns:
        [pd.Dataframe] rows are months (0-11), cols are ["Cost ($)","Consumed Power (GWh)","Renewable Power Used (%)"]
    """
    
    # this will be the return value 
    optimization_result = pd.DataFrame(0, index=const.MONTHS_INDICES, columns=["Cost ($)","Consumed Power (GWh)","Renewable Power Used (%)"])
    
    # local copy of the predicted power needs
    local_predicted_data = predicted_data.copy(deep=True)
    
    for month in const.MONTHS_INDICES:
      # how much production per zone per source in this month is left
      days = const.DAYS_IN_MONTH[month] # days in the month
      power_produced = self._plantProductionRates.copy(deep=True).apply(lambda x: x * days * 24 / 1000) #GWh
      
      # total needed for zone in this month
      power_needed = local_predicted_data.iloc[month] # GWh
      
      # total power to/from in each zone for this month
      power_sent_matrix = pd.DataFrame(0, index=const.PENALTY_ZONES, columns=const.PENALTY_ZONES) # GWh
      
      # emmissions received in each zone for this month
      emission_table = pd.DataFrame(0, index=const.PENALTY_ZONES, columns=["emissive", "non-emissive"]) # GWh

      # update the above tables based on moving power between zones
      renewable_consumption, non_renewable_consumption = self._power_province(power_produced, power_needed, power_sent_matrix, emission_table)
      
      # update the above tables based on selling 
      self._sell_power(power_produced, power_sent_matrix, emission_table)
      
      # calculate cost this month
      cost = self._calculate_cost(power_sent_matrix, emission_table)
      optimization_result["Cost ($)"].iloc[month] = cost
      
      # Calculate renewable %
      monthly_renewable = 100 * renewable_consumption / (renewable_consumption + non_renewable_consumption) 
      optimization_result["Renewable Power Used (%)"].iloc[month] = monthly_renewable
      
    
    # Calculate total consumption for all months
    total_consumption_per_month = predicted_data.sum(axis=1)
    optimization_result["Consumed Power (GWh)"] = total_consumption_per_month
    
    return optimization_result


  def _power_province(self, power_produced, power_needed, power_sent_matrix, emission_table):
    """Moves power between zones. Modifies args by reference.

    Args:
        power_produced ([pd.Dataframe]): power produced in each zone
        power_needed ([pd.Dataframe]): power needed for each zone
        power_sent_matrix ([pd.Dataframe]): a matrix containing how much power was sent between all zones
        emission_table ([pd.Dataframe]): a table containing how much power consumed in each zone was emissive and non-emissive

    Returns:
        [tuple(float,float)]: total renewable_consumption and non_renewable_consumption in the province
    """    
    
    # total renewable energy consumed in the province 
    renewable_consumption = 0
    # total non-renewable energy consumed in the province 
    non_renewable_consumption = 0
    
    for penalty, fromZone, toZone in self._sorted_penalties:
      # move power between zones
      if power_needed[toZone] <= 0:
        continue

      fromZoneIdx = int(fromZone[-1]) -1 # convert Z1 to 0
      toZoneIdx = int(toZone[-1]) - 1
      zone_production = power_produced.iloc[fromZoneIdx] 

      for source in const.ORDERED_PLANT_TYPES:
        source_produced = zone_production[source]
        power_given = min(power_needed[toZone], source_produced)
        zone_production[source] -= power_given
        power_needed[toZone] -= power_given
        power_sent_matrix[fromZone].iloc[toZoneIdx] += power_given
        
        # keep track of emissive power sent to zones
        emmission_key = "emissive" if source in const.EMITTING_PLANTS else "non-emissive"
        emission_table[emmission_key].iloc[toZoneIdx] += power_given
        
        # keep track of renewable energy consumed in province
        if source in const.RENEWABLE_PLANTS: 
          renewable_consumption += power_given
        else: 
          non_renewable_consumption += power_given
        
        if power_needed[toZone] <= 0:
          break        
    return renewable_consumption, non_renewable_consumption
  
  
  def _sell_power(self, power_produced, power_sent_matrix, emission_table):
    """Determins where the excess power should be sold. Modifies args by reference.

    Args:
        power_produced ([pd.Dataframe]): power produced in each zone
        power_sent_matrix ([pd.Dataframe]): a matrix containing how much power was sent between all zones
        emission_table ([pd.Dataframe]): a table containing how much power consumed in each zone was emissive and non-emissive
    """    
    # itterate over all power production values
    for fromZoneIdx, row in power_produced.iterrows():
      for source in row.index.values:  
        excess_power = row[source]        
        if excess_power > 0: # if source still has excess power             
          if source not in const.DISSIPATING_POWER_PLANTS: # if you can dissipate, do not sell 
            
            # send power to cheapest external zone
            zone_str = f'Z{fromZoneIdx+1}'
            cheapestDestinationZoneIdx = self._cheapest_external_penalties[zone_str]
            power_sent_matrix[zone_str].iloc[cheapestDestinationZoneIdx] += excess_power
            
            # keep track of emissive power sent to zones
            emmission_key = "emissive" if source in const.EMITTING_PLANTS else "non-emissive"
            emission_table[emmission_key].iloc[cheapestDestinationZoneIdx] += excess_power
          power_produced[source].iloc[fromZoneIdx] = 0 # power sold or dissipated


  def _calculate_cost(self, power_sent_matrix, emission_table):
    """Calculates the cost of powering one zone for one month

    Args:
        power_sent_matrix ([pd.Dataframe]): a matrix containing how much power was sent between all zones
        emission_table ([pd.Dataframe]): a table containing how much power consumed in each zone was emissive and non-emissive

    Returns:
        [float]: total cost incurred in all province zones
    """    
    total_cost = 0.0
    for zone in const.PENALTY_ZONES:
      power_costs = np.dot(self._penaltyValues[zone], const.GW_TO_KW * power_sent_matrix[zone])
      zone_net_emission = emission_table['emissive'].loc[zone]
      emission_tax = float(self._emissionTax) * const.GW_TO_KW * zone_net_emission
      incentive = float(self._nonEmissiveIncentive) * const.GW_TO_KW * emission_table['non-emissive'].loc[zone]
      zone_total_cost = power_costs + emission_tax - incentive
      total_cost += zone_total_cost
    return total_cost

