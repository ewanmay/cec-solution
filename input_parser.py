import numpy as np
import pandas as pd
import const
import pathlib
path = pathlib.Path(__file__).parent.absolute()


def parseInputs():
    """Loads all the input files into pandas data frames with the correct row and column names. 
    Returns:
        data, emissionTax, nonEmissiveIncentive, penaltyValues, plantProductionRates
    """    
    # Import past year's data
    data = {} # {year: df}
    # df row indices are months 0-11. colums are zones Z1-Z7
    # values are energy consumption in that month in that zone, in GWh
    for year in const.DATA_YEARS:
        data[year] = pd.read_csv(f'{path}/{const.DATA_DIR}/NBTrend20{year}.csv', names=const.ZONES)

    # Import Incentive Rates 
    incentiveRates = pd.read_csv(f'{path}/{const.INFO_DIR}/IncentiveRates.csv') 
    emissionTax, nonEmissiveIncentive = incentiveRates.columns # $/kWh

    # Import Penalty Values
    penaltyValues = pd.read_csv(f'{path}/{const.INFO_DIR}/PenaltyValues.csv', names=const.PENALTY_ZONES)

    # Import Plant Production Rates
    plantProductionRates = pd.read_csv(f'{path}/{const.INFO_DIR}/PlantProductionRates.csv', names=const.PLANT_TYPES)

    return data, emissionTax, nonEmissiveIncentive, penaltyValues, plantProductionRates





