import os
import csv
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseYNABConverter:
    """Base converter for mapping CSV files into YNAB format."""
    COLUMNS_TO_GRAB = ['date', 'payee', 'memo', 'outflow', 'inflow']

    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.base_name = os.path.splitext(os.path.basename(input_file))[0]
        self.output_file = os.path.join(
            output_dir, f"{self.base_name}_ynab.csv"
        )

    def map_row(self, row):
        """Map a single row to YNAB format. Subclasses override this."""
        raise NotImplementedError

    def convert(self):
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.input_file, 'r') as input_file, \
             open(self.output_file, 'w', newline='') as output_file:

            reader = csv.DictReader(input_file)
            writer = csv.DictWriter(output_file, fieldnames=self.COLUMNS_TO_GRAB)
            writer.writeheader()

            for row in reader:
                # Defensive: skip rows that are not dicts or are empty
                if not isinstance(row, dict) or not row:
                    continue
                # Defensive: skip rows where all values are None or empty
                if all((v is None or v == '') for v in row.values()):
                    continue
                ynab_row = {col: '' for col in self.COLUMNS_TO_GRAB}
                try:
                    mapped = self.map_row(row)
                except Exception as e:
                    logger.warning(f"[ynab_converter] Skipping malformed row: {row} ({e})")
                    continue
                if not isinstance(mapped, dict):
                    continue
                ynab_row.update(mapped)
                writer.writerow(ynab_row)

        logger.info(f"[ynab_converter] {self.input_file} → {self.output_file}")


class BHDYNABConverter(BaseYNABConverter):
    def map_row(self, row):
        outflow = row.get('outflow', '').strip().replace('$', '').replace(',', '').strip()
        inflow = row.get('inflow', '').strip().replace('$', '').replace(',', '').strip()
        return {
            'date': row.get('date', ''),
            'payee': '',
            'memo': row.get('memo', ''),
            'outflow': abs(float(outflow)) if outflow else '',
            'inflow': abs(float(inflow)) if inflow else ''
        }


class BPDAccYNABConverter(BaseYNABConverter):
    def map_row(self, row):
        if not row or not isinstance(row, dict):
            return {}
        type_val = row.get('type')
        # Defensive: skip if type_val is not a string or is None
        if type_val is None:
            return {}
        type_str = str(type_val).upper()
        ynab_row = {
            'date': row.get('date', ''),
            'payee': '',
            'memo': row.get('memo', ''),
        }
        if type_str == 'DB':
            ynab_row['outflow'] = f"{float(row.get('amount', 0) or 0):.2f}"
        elif type_str == 'CR':
            ynab_row['inflow'] = f"{float(row.get('amount', 0) or 0):.2f}"
        return ynab_row


class BPDTcYNABConverter(BaseYNABConverter):
    def map_row(self, row):
        if not row or not isinstance(row, dict):
            return {}
        type_val = row.get('type')
        if type_val is None:
            return {}
        type_str = str(type_val).upper()
        current_year = datetime.now().year
        date = row.get('date', '')
        ynab_row = {
            'date': f"{date}/{current_year}" if date else '',
            'payee': '',
            'memo': row.get('memo', ''),
        }
        if type_str == 'CR':
            ynab_row['outflow'] = f"{float(row.get('amount', 0) or 0):.2f}"
        else:
            ynab_row['inflow'] = f"{float(row.get('amount', 0) or 0):.2f}"
        return ynab_row


class YNABFileProcessor:
    converters = {
        'bhd': BHDYNABConverter,
        'bpd acc': BPDAccYNABConverter,
        'bpd tc': BPDTcYNABConverter,
    }

    @staticmethod
    def detect_and_convert_all(result_dir, ynab_dir):
        os.makedirs(ynab_dir, exist_ok=True)
        for filename in os.listdir(result_dir):
            file_path = os.path.join(result_dir, filename)
            if not os.path.isfile(file_path) or not filename.endswith('.csv'):
                continue

            filename_lower = filename.lower()
            if filename_lower.startswith('bhd'):
                converter_cls = YNABFileProcessor.converters['bhd']
            elif filename_lower.startswith('bpd') and 'acc' in filename_lower:
                converter_cls = YNABFileProcessor.converters['bpd acc']
            elif filename_lower.startswith('bpd') and 'tc' in filename_lower:
                converter_cls = YNABFileProcessor.converters['bpd tc']
            else:
                logger.info(f"[ynab_converter] Skipped unknown format: {filename}")
                continue

            converter_cls(file_path, ynab_dir).convert()