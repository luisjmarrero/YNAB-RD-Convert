import csv
import io
import os
import logging

logger = logging.getLogger(__name__)


def _format_date(raw):
    """Convert YYYYMMDD to MM/DD/YYYY."""
    d = raw.strip()
    if len(d) == 8 and d.isdigit():
        return f"{d[4:6]}/{d[6:8]}/{d[:4]}"
    return d


def _read_utf16le(path):
    """Read a UTF-16LE file (no BOM) and return decoded text."""
    with open(path, 'rb') as f:
        raw = f.read()
    return raw.decode('utf-16-le')


class PervAcctConverter:
    """Converts Peravia savings account CSV (UTF-16LE encoded) to intermediate CSV."""

    headers = ['date', 'reference', 'memo', 'amount', 'type']

    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.base_name = os.path.splitext(os.path.basename(input_file))[0]
        self.output_file = os.path.join(output_dir, f"{self.base_name}.csv")

    def convert(self):
        text = _read_utf16le(self.input_file)

        with io.StringIO(text) as txt_file, \
             open(self.output_file, 'w', newline='') as csv_file:

            reader = csv.reader(txt_file)
            writer = csv.writer(csv_file)
            writer.writerow(self.headers)

            header_skipped = False
            for row in reader:
                if not header_skipped:
                    header_skipped = True
                    continue

                row = [cell.strip() for cell in row]
                if not row or all(c == '' for c in row):
                    continue

                date = _format_date(row[0])
                reference = row[2].strip()
                desc = row[3].strip()
                desc2 = row[4].strip() if row[4].strip() else ''
                desc3 = row[5].strip() if row[5].strip() else ''
                memo = ' '.join(filter(None, [desc, desc2, desc3]))
                tipo = row[6].strip()
                amount = row[7].strip()

                writer.writerow([date, reference, memo, amount, tipo])

        logger.info(f"[perv_converter] {self.input_file} → {self.output_file}")


class PervFileProcessor:
    """Detects file type and delegates to the right converter."""

    converters = {
        'acc': PervAcctConverter,
    }

    @staticmethod
    def convert_file(input_file, output_dir):
        base_name_lower = os.path.splitext(os.path.basename(input_file))[0].lower()
        for key, converter_cls in PervFileProcessor.converters.items():
            if key in base_name_lower:
                converter_cls(input_file, output_dir).convert()
                return
        logger.warning(f"[perv_converter] Skipped unknown format: {input_file}")
