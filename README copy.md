# Restigouche CEC 2021

## Setup

To install all dependent python libraies, run the following command.
```
pip install -r requirements.txt
```

Ensure that the `.csv` files of past year data are in `./PastYearData` and that the `.csv` files of information are in `./Information`.

## Run the Program

Run the main driver of the program using the following command.
```
python restigouche_driver.py
```

## Outputs

The application generates output files to the `./ExportData` directory, namely the energy consumption predictions CSV (which will be named by the year to predict, eg. `2022_prediction.csv`) for Level 1 and the `optimization_result.csv` for Level 2.

The Level 1 output file shows the predicted power usage forecasted for each zone in the province (columns), for each month of the year (rows).

The Level 2 output file displays the Cost ($), Total Consumed Power (GWh), and Renewable Power Used (%) for the province (columns) for each month (rows).