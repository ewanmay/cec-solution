import os
import numpy as np
import pandas as pd
from const import DATA_YEARS, ZONES, MONTHS_INDICES, EXPORT_DIR
import matplotlib.pyplot as plt
import pathlib
path = pathlib.Path(__file__).parent.absolute()


class PredictionModel():
  
  def __init__(self, yearly_data):
    self.predictors = self._getLinearValues(yearly_data)

  def _getLinearValues(self, yearly_data):
    """

    Prediction of next year's energy consumption based on past year's data
inutP
            
    # for year gs cons:.DATA_YEARS:
    #     year = pd.read_csv(f'{inputPath}/NBTrend20{year}.csv', names=const.ZONES
        yearly_data (pd.DataFrame): representing each month's energy usage data per zone

    Returns:
        [dict<dict<number: lambda>>]: Returns a dictionary of zones th
    emissionTax = float(emissionTax)
    nonEmissiveIncentive = float(nonEmissiveIncentive)at each have a dictionary 
                                      with keys months and and values of linear fit variables
    """    
    
    energy_per_zone_per_month = {zone: {} for zone in ZONES} 
    
    # For each year and for each zone, ag the monthly data in an array
    for year in DATA_YEARS:
      for zone in ZONES:
        for month in MONTHS_INDICES:

          # Current aggregation
          aggregated_monthly_zone = energy_per_zone_per_month[zone]

          # Past value to aggregate
          zone_month_energy_used = yearly_data[year][zone][month]
          
          if not month in aggregated_monthly_zone:
            aggregated_monthly_zone[month] = [zone_month_energy_used]
          else:
            aggregated_monthly_zone[month].append(zone_month_energy_used)
    
    linear_fit_variables = {zone: {} for zone in ZONES}  
    
    for zone in ZONES:
      for month in MONTHS_INDICES:  
        month_values = energy_per_zone_per_month[zone][month]
        # Generate linear extrapolation constants for each month - zone set of data
        m, b = np.polyfit(x=np.array(DATA_YEARS), y=np.array(month_values), deg=1)         
        linear_fit_variables[zone][month] = (m, b)

    return self._macroFactor(linear_fit_variables)

  def _macroFactor(self, linear_fit_variables):
    """Aggregate all linear extrapolation functions for a macrotrend of New Brunswick

    Args:
        linear_fit_variables (dict<dict<string, array<int>>>): Linear Fit Variables using only monthly zone trends 

    Returns:
        linear_fit_variables (dict<dict<string, array<int>>>): Linear Fit Variables using only monthly zone trends while factoring in macro trends
    """    

    macrofactor = 0
    factors_taken = 0
    # Factor in the overall trend of New Brunswick on the Macro Scale
    for zone in ZONES:
      for month in MONTHS_INDICES:
        factors_taken += 1
        (m, b) = linear_fit_variables[zone][month]
        macrofactor += m
    
    macrofactor /= factors_taken    

    # Factor in the overall trend of New Brunswick on the Macro Scale
    for zone in ZONES:
      for month in MONTHS_INDICES:        
        (m, b) = linear_fit_variables[zone][month]
        linear_fit_variables[zone][month] = (m * 0.85 + 0.15 * macrofactor, b)

    return linear_fit_variables

  def _predict(self, zone, month, year):    
    """predict the energy usage for a given zone, month, year

    Args:
        zone ([string]): [Zone string, i.e Zone one = 'Z1']
        month ([integer]): [Month requested on a scale from 0 to 11, where 0 is January and 11 is December]
        year ([int]): [Year requested to predict]

    Returns:
        [float]: [Energy usage prediction for that zone and month of the year provided]
    """    
    m, b = self.predictors[zone][month]
    return m * year + b

  def predictYear(self, year, save_csv=True):
    """predict the energy usages for each month and zone for the given year

    Args:
        year ([int]): [Year requested to predict]

    Returns:
        [pd.DataFrame]: [Energy usages for each month (row) and zone (col) for the given year]
    """

    year = int(year)
    use_year = year
    if year > 2000:
      use_year -= 2000
    results = {zone: {} for zone in ZONES} 
    for zone in results.keys():
      for month in MONTHS_INDICES:
        results[zone][month] = self._predict(zone, month, use_year)

    results_df = pd.DataFrame.from_dict(results)
    return results_df


  def _plotExample(self, year):
    """plot the energy usages for each month in Z1 for a few years around the given year

    Args:
        year ([int]): [Year requested to plot]
    """
    x = MONTHS_INDICES
    for disp_year in range(year - 3, year + 1):
      y = [self._predict('Z1', m, disp_year) for m in MONTHS_INDICES]
      plt.plot(x, y)
    
    plt.xlabel("month")
    plt.ylabel("energy")
    plt.show()


if __name__ == "__main__":
  # this MAIN just for testing
  DATA_DIR = 'PastYearData'
  data = {}
  for year in DATA_YEARS:
    data[year] = pd.read_csv(f'{path}\\{DATA_DIR}\\NBTrend20{year}.csv', names=ZONES)        
  model = PredictionModel(data)      
  year_df = model.predictYear(2022, False)
  
  month = 11
  varsForPlot = [data[year]['Z1'][month] for year in data]
  varsForPlot.append(year_df['Z1'][month])
  plt.figure()
  plt.plot([2015, 2016, 2017, 2018, 2022], varsForPlot)   
  (m, b) = model.predictors['Z1'][month]
  x = np.array([19, 20, 21, 22])
  plt.plot([2019, 2020,2021, 2022], m * x.astype(float) + b)  
  plt.title("Zone 1, December 2022 prediction")
  plt.legend(["Past and prediction", "Linear extrapolation"])
  plt.xlabel("Year")
  plt.ylabel("Energy (GWh)")
  plt.show()

    