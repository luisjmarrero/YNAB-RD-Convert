import csv
import os
import logging

logger = logging.getLogger(__name__)

class BPDBaseConverter:
    """Base class for converting BPD text files to CSV."""
    
    headers = []  # Override in subclasses
    trim_last_n_cols = 0  # Override if we need to drop columns

    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.base_name = os.path.splitext(os.path.basename(input_file))[0]
        self.output_file = os.path.join(output_dir, f"{self.base_name}.csv")

    def convert(self):
        """Main entry point for conversion."""
        try:
            with open(self.input_file, 'r') as txt_file, \
                 open(self.output_file, 'w', newline='') as csv_file:

                writer = csv.writer(csv_file)
                writer.writerow(self.headers)

                for line in txt_file:
                    line = line.strip()
                    if not line or line == "Consumos Regulares":
                        continue

                    row = [field.strip().strip('"') for field in line.split(',')]
                    if self.trim_last_n_cols > 0:
                        row = row[:-self.trim_last_n_cols]
                    writer.writerow(row)

            logger.info(f"[bpd_converter] {self.input_file} → {self.output_file}")
        except Exception as e:
            logger.error(f"[bpd_converter] Error converting {self.input_file}: {e}")


class BPDAcctConverter(BPDBaseConverter):
    headers = ['account', 'date', 'reference', 'amount', 'type', 'memo']
    trim_last_n_cols = 2


class BPDCreditCardConverter(BPDBaseConverter):
    headers = ['card', 'date', 'reference', 'amount', 'type', 'memo']
    trim_last_n_cols = 0


class BPDFileProcessor:
    """Detects file type and delegates to the right converter."""
    
    converters = {
        'acc': BPDAcctConverter,
        'tc': BPDCreditCardConverter,
    }

    @staticmethod
    def convert_file(input_file, output_dir):
        base_name_lower = os.path.splitext(os.path.basename(input_file))[0].lower()
        for key, converter_cls in BPDFileProcessor.converters.items():
            if key in base_name_lower:
                converter_cls(input_file, output_dir).convert()
                return
        logger.warning(f"[bpd_converter] Skipped unknown format: {input_file}")