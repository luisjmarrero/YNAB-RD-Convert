import csv
import os


def _handle_acc(input_file, output_dir):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}.csv")

    headers = ['account', 'date', 'reference', 'amount', 'type', 'memo']

    with open(input_file, 'r') as txt_file, open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)

        for line in txt_file:
            line = line.strip()
            if not line or line == "Consumos Regulares":
                continue
            # Split the line by ',' and strip spaces or quotes from each field
            row = [field.strip().strip('"') for field in line.split(',')]
            # Exclude the last 2 columns (balance)
            writer.writerow(row[:-2])

        print(f"[bpd] {input_file} -> {output_file}")


def _handle_tc(input_file, output_dir):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}.csv")

    # set headers
    headers = ['card', 'date', 'reference', 'amount', 'type', 'memo']

    with open(input_file, 'r') as txt_file, open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(headers)

        for line in txt_file:
            line = line.strip()
            if not line or line == "Consumos Regulares":
                continue
            # Split the line by ',' and strip spaces or quotes from each field
            row = [field.strip().strip('"') for field in line.split(',')]
            writer.writerow(row)

        print(f"[bpd] {input_file} -> {output_file}")


def convert_bpd_file_to_csv(input_file, output_dir):
    try:
        base_name = os.path.splitext(os.path.basename(input_file))[0].lower()

        if 'acc' in base_name:
            _handle_acc(input_file, output_dir)
        elif 'tc' in base_name:
            _handle_tc(input_file, output_dir)
        else:
            print(f"[bpd] Skipped unknown format: {input_file}")
            return

        print(f"[bpd] {input_file} → {os.path.join(output_dir, f'{base_name}.csv')}")
    except Exception as e:
        print(f"Popular Error converting {input_file}: {e}")
