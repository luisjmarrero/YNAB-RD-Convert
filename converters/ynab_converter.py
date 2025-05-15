import os
import csv
from datetime import datetime

RESULT_DIR = 'result'
YNAB_DIR = os.path.join(RESULT_DIR, 'ynab')
COLUMNS_TO_GRAB = ['date', 'payee', 'memo', 'outflow', 'inflow']


def ensure_ynab_dir():
    if not os.path.exists(YNAB_DIR):
        os.makedirs(YNAB_DIR)


def convert_to_ynab_format():
    current_year = datetime.now().year

    for filename in os.listdir(RESULT_DIR):
        file_path = os.path.join(RESULT_DIR, filename)

        # Skip directories and non-CSV files
        if not os.path.isfile(file_path) or not filename.endswith('.csv'):
            continue

        ynab_file_path = os.path.join(YNAB_DIR, f"{os.path.splitext(filename)[0]}_ynab.csv")

        with open(file_path, 'r') as input_file, open(ynab_file_path, 'w', newline='') as output_file:
            reader = csv.DictReader(input_file)
            writer = csv.DictWriter(output_file, fieldnames=COLUMNS_TO_GRAB)
            writer.writeheader()

            for row in reader:
                ynab_row = {col: '' for col in COLUMNS_TO_GRAB}  # Initialize empty row

                # Mapping logic for `bhd` files
                if filename.startswith('bhd'):
                    ynab_row['date'] = row.get('date', '')
                    ynab_row['payee'] = ''  # Payee is empty
                    ynab_row['memo'] = row.get('memo', '')
                    ynab_row['outflow'] = abs(float(row.get('outflow', 0))) if row.get('outflow') else ''
                    ynab_row['inflow'] = abs(float(row.get('inflow', 0))) if row.get('inflow') else ''

                # Mapping logic for `bpd acc` files
                elif filename.startswith('bpd') and 'acc' in filename:
                    ynab_row['date'] = row.get('date', '')
                    ynab_row['payee'] = ''  # Payee is empty
                    ynab_row['memo'] = row.get('memo', '')
                    if row.get('type', '').upper() == 'DB':
                        ynab_row['outflow'] = f"{float(row.get('amount', 0)):.2f}"
                    elif row.get('type', '').upper() == 'CR':
                        ynab_row['inflow'] = f"{float(row.get('amount', 0)):.2f}"

                # Mapping logic for `bpd tc` files
                elif filename.startswith('bpd') and 'tc' in filename:
                    date = row.get('date', '')
                    ynab_row['date'] = f"{date}/{current_year}" if date else ''
                    ynab_row['payee'] = ''  # Payee is empty
                    ynab_row['memo'] = row.get('memo', '')
                    if row.get('type', '').upper() == 'CR':
                        ynab_row['outflow'] = f"{float(row.get('amount', 0)):.2f}"
                    else:
                        ynab_row['inflow'] = f"{float(row.get('amount', 0)):.2f}"

                writer.writerow(ynab_row)

        print(f"[ynab] {file_path} → {ynab_file_path}")