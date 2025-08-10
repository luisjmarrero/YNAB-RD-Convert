import os
import csv
import pdfplumber
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Suppress pdfplumber warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)


class BHDBaseConverter:
    """Base class for converting BHD PDF files to CSV."""

    headers = []
    file_suffix = None  # For subclasses that create multiple files (like TC)

    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.base_name = os.path.splitext(os.path.basename(input_file))[0]

    def convert(self):
        raise NotImplementedError("Subclasses must implement convert()")


class BHDAcctConverter(BHDBaseConverter):
    headers = ['date', 'reference', 'memo', 'outflow', 'inflow']

    def convert(self):
        output_file = os.path.join(self.output_dir, f"{self.base_name}.csv")

        with pdfplumber.open(self.input_file) as pdf, open(output_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.headers)
            logger.info(f"[bhd_converter] Processing {self.input_file}...")

            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    for row in table:
                        if len(row) < 5:
                            continue
                        if "Fecha" in row[0] or "Número de Referencia" in row[0]:
                            continue

                        row = [cell.strip() if cell else "" for cell in row]
                        outflow = row[3].replace("US", "").replace("RD", "").replace(",", "").strip()
                        inflow = row[4].replace("US", "").replace("RD", "").replace(",", "").strip()

                        date, reference, memo = row[:3]
                        writer.writerow([date, reference, memo, outflow, inflow])

        logger.info(f"[bhd_converter] {self.input_file} → {output_file}")


class BHDCreditCardConverter(BHDBaseConverter):
    headers = ['auth_number', 'date', 'application_date', 'memo', 'currency', 'outflow', 'inflow']

    def convert(self):
        base_name_lower = self.base_name.lower()
        currency_data = defaultdict(list)

        with pdfplumber.open(self.input_file) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    for row in table:
                        if len(row) < 7:
                            continue

                        row = [cell.strip() if cell else "" for cell in row]
                        outflow = row[5].replace(",", "").strip()
                        inflow = row[6].replace(",", "").strip()
                        currency = row[4]

                        currency_data[currency].append([
                            row[0], row[1], row[2], row[3], currency, outflow, inflow
                        ])

        for currency, rows in currency_data.items():
            if not currency or currency.strip() == "":
                logger.warning(f"[bhd_converter] Skipped empty currency in {self.input_file}")
                continue

            output_file = os.path.join(
                self.output_dir, f"{base_name_lower}_{currency.lower()}.csv"
            )
            logger.info(f"[bhd_converter] Writing {output_file} for currency: {currency}")

            with open(output_file, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(self.headers)
                writer.writerows(rows)

        logger.info(f"[bhd_converter] {self.input_file} → multiple CSVs")


class BHDFileProcessor:
    """Detects file type and delegates to the right converter."""

    converters = {
        'acc': BHDAcctConverter,
        'tc': BHDCreditCardConverter,
    }

    @staticmethod
    def convert_file(input_file, output_dir):
        base_name_lower = os.path.splitext(os.path.basename(input_file))[0].lower()
        for key, converter_cls in BHDFileProcessor.converters.items():
            if key in base_name_lower:
                converter_cls(input_file, output_dir).convert()
                return
        logger.warning(f"[bhd] Skipped unknown format: {input_file}")
