import os
import csv
import pdfplumber
import logging
from collections import defaultdict

# Suppress pdfplumber warnings
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


def _handle_acc(input_file, output_dir):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}.csv")

    headers = ['date', 'reference', 'memo', 'outflow', 'inflow']  # Desired CSV headers

    with pdfplumber.open(input_file) as pdf, open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)  # Write the CSV headers

        for page in pdf.pages:
            tables = page.extract_tables()  # Extract tables from the page
            for table in tables:
                for row in table:
                    # Skip rows that don't match the expected number of columns
                    if len(row) < 5:
                        continue

                    if "Fecha" in row[0] or "Número de Referencia" in row[0]:
                        continue

                    # Handle None values and clean up the row
                    row = [cell.strip() if cell else "" for cell in row]

                    # Remove "RD" prefix and format numbers
                    outflow = row[3].replace("RD", "").replace(",", "").strip()
                    inflow = row[4].replace("RD", "").replace(",", "").strip()

                    # Map the table row to the desired CSV format
                    date, reference, memo = row[:3]
                    writer.writerow([date, reference, memo, outflow, inflow])

        print(f"[pdf] {input_file} → {output_file}")


def _handle_tc(input_file, output_dir):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    headers = ['auth_number', 'date', 'application_date', 'memo', 'currency', 'outflow', 'inflow']

    currency_data = defaultdict(list)  # Group rows by currency

    with pdfplumber.open(input_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()  # Extract tables from the page
            for table in tables:
                for row in table:
                    # Skip rows that don't match the expected number of columns
                    if len(row) < 7:
                        continue

                    # Handle None values and clean up the row
                    row = [cell.strip() if cell else "" for cell in row]

                    # Remove "RD" or "US" prefix from outflow and inflow and format numbers
                    outflow = row[5].replace(",", "").strip()
                    inflow = row[6].replace(",", "").strip()

                    # Group rows by currency
                    currency = row[4]
                    currency_data[currency].append([row[0], row[1], row[2], row[3], currency, outflow, inflow])

    # Write separate CSV files for each currency
    for currency, rows in currency_data.items():
        output_file = os.path.join(output_dir, f"{base_name.lower()}_{currency.lower()}.csv")
        with open(output_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)  # Write the CSV headers
            writer.writerows(rows)  # Write the rows for the currency

        print(f"[pdf] {input_file} → {output_file}")


def convert_bhd_file_to_csv(input_file, output_dir):
    try:
        base_name = os.path.splitext(os.path.basename(input_file))[0].lower()

        if 'acc' in base_name:
            _handle_acc(input_file, output_dir)
        elif 'tc' in base_name:
            _handle_tc(input_file, output_dir)
        else:
            print(f"[bhd] Skipped unknown format: {input_file}")
            return

    except Exception as e:
        print(f"BHD: Error converting {input_file}: {e}")
