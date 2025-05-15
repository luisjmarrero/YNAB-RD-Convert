# YNAB RD Convert Tool

This script converts bank transaction data into a format compatible with YNAB (You Need A Budget). It processes CSV files from various banks, mapping their columns to YNAB's required format.

## Supported Banks

- BHD:
  - bhd files: Standard format with date, memo, inflow, and outflow.
  - bhd tc files: Ensures outflow and inflow are always positive.
- BPD:
  - bpd acc files: Maps type to outflow or inflow and formats them as numbers.
  - bpd tc files: Adds the current year to the date and formats outflow and inflow as numbers.

## How to Use the Script
1. Place your bank files in the data folder.
  - For BHD, use the format: `bhd_{your_name}tc.pdf` for credit card files or `bhd_{your_name}_acc.pdf` for account files.
  - For BPD (Banco Popular), use the format: `bpd_{your_name}tc.pdf` for credit card files or `bpd_{your_name}_acc.pdf` for account files.
2. Run the script using:
```shell
python main.py
```
3. Processed files will be saved in the result/ynab folder with _ynab appended to their names.

### How to Clear Up the Data

- The result folder is cleared automatically on each run to ensure no leftover data interferes with the new results. Or can be cleared manually by calling 
```shell
./bin/clear_result.sh
```
or to clear the data folder
```shell
./bin/clear_data.sh
```