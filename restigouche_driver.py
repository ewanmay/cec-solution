import sys, os
from input_parser import parseInputs
from prediction_model import PredictionModel
from optimization_model import OptimizationModel
from const import EXPORT_DIR, DATA_DIR

def main():
    # try:
    year = None
    exportDirectory = None
    inputDirectory = None
    if len(sys.argv) > 1:
        year = sys.argv[1]
        exportDirectory = sys.argv[2]
        inputDirectory = sys.argv[3]

    # Set system    
    if not inputDirectory:
        inputDirectory = DATA_DIR
    if not exportDirectory:
        exportDirectory = EXPORT_DIR
    if not year:
        year = 2022

    yearlyZoneEnergyData, emissionTax, nonEmissiveIncentive, penaltyValues, plantProductionRates = parseInputs()
    # predict - Level 1
    prediction_model = PredictionModel(yearlyZoneEnergyData)    
    prediction_df = prediction_model.predictYear(year)
    # output Level 1 CSV
    prediction_df.to_csv(f'{exportDirectory}/{year}_prediction.csv', header=False, index=False)

    # calculate optimizations - Level 2
    optimization_model = OptimizationModel(emissionTax, nonEmissiveIncentive, penaltyValues, plantProductionRates)
    optimization_result = optimization_model.optimize(prediction_df)
    # output Level 2 CSV
    optimization_result.to_csv(f'{exportDirectory}/optimization_result.csv', header=False, index=False)
    # except:
    #     print("An error occurred.")
    #     print("Please make sure you are calling the program correctly: [python] ./restigouche_driver.py [year] [path_to_past_data] [path_to_output(local)]")


if __name__ == "__main__":
    main()
