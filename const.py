DATA_DIR = './PastYearData'
INFO_DIR = './Information'
EXPORT_DIR = './ExportData'

GW_TO_KW = 1e6

DATA_YEARS = [15,16,17,18]
ZONES = [f'Z{i}' for i in range(1,7+1)]
PENALTY_ZONES = [f'Z{i}' for i in range(1,11+1)]
EXTERNAL_ZONE_INDICES = range(7,11)
PLANT_TYPES = ['Thermal', 'Nuclear', 'Combustion Turbine', 'Hydro', 'Wind']
ORDERED_PLANT_TYPES = ['Wind', 'Hydro', 'Thermal', 'Combustion Turbine', 'Nuclear']
EMITTING_PLANTS = ['Thermal', 'Combustion Turbine']
RENEWABLE_PLANTS = ['Wind', 'Hydro']
DISSIPATING_POWER_PLANTS = ['Nuclear']

MONTHS_INDICES = [month for month in range(0, 12)]
DAYS_IN_MONTH = {0: 31, 1: 28, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 30, 8: 31, 9: 30, 10: 31, 11: 30,}