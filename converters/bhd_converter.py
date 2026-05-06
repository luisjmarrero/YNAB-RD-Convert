import os
import csv
import re
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
        amount_pattern = re.compile(r'(US|RD)\$?\s*([\d,.-]+)')

        with pdfplumber.open(self.input_file) as pdf:
            logger.info(f"[bhd_tc] PDF has {len(pdf.pages)} page(s)")

            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables() or []
                logger.info(f"[bhd_tc] Page {page_num}: {len(tables)} table(s) found via extract_tables()")

                if not tables:
                    # Try with explicit table settings for PDFs without visible grid lines
                    tables = page.extract_tables({
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    }) or []
                    logger.info(f"[bhd_tc] Page {page_num}: {len(tables)} table(s) found with text strategy")

                if not tables:
                    # Fallback: try to parse text lines directly
                    text = page.extract_text()
                    if text:
                        logger.info(f"[bhd_tc] Page {page_num}: falling back to text extraction")
                        rows = self._parse_text_lines(text, amount_pattern)
                        for parsed_row in rows:
                            currency_data[parsed_row[4]].append(parsed_row)
                    continue

                for table_idx, table in enumerate(tables):
                    logger.info(f"[bhd_tc] Page {page_num}, Table {table_idx}: {len(table)} row(s)")
                    for row in table:
                        if len(row) < 5:
                            continue

                        row = [cell.strip() if cell else "" for cell in row]

                        # Skip header rows (flexible matching)
                        if any(h in row[0] for h in ["Autorización", "Autorizaci"]) or \
                           any(h in row[1] for h in ["Fecha", "Transacción", "Transacci"]):
                            continue

                        currency = ""
                        outflow = ""
                        inflow = ""

                        if len(row) >= 7 and row[4] in ('US', 'RD'):
                            # 7-col format: [auth, date, app_date, memo, currency, debit, credit]
                            # Amounts are plain numbers; credits stored as negative values
                            currency = row[4]
                            debit_val = row[5].replace(',', '').strip()
                            credit_val = row[6].replace(',', '').strip()
                            outflow = debit_val if debit_val and debit_val != '0' else ''
                            if credit_val and credit_val != '0':
                                inflow = credit_val.lstrip('-')
                        else:
                            # 6-col format: currency embedded in amount strings (e.g. "RD$ 2,040.00")
                            debit_raw = row[4] if len(row) > 4 else ""
                            credit_raw = row[5] if len(row) > 5 else ""

                            if debit_raw:
                                m = amount_pattern.search(debit_raw)
                                if m:
                                    currency = m.group(1)
                                    outflow = m.group(2).replace(",", "")
                            if credit_raw:
                                m = amount_pattern.search(credit_raw)
                                if m:
                                    currency = m.group(1)
                                    inflow = m.group(2).replace(",", "")

                            if not currency:
                                for i, cell in enumerate(row):
                                    m = amount_pattern.search(cell)
                                    if m:
                                        currency = m.group(1)
                                        logger.debug(f"[bhd_tc] Found currency in column {i}: {cell}")
                                        break

                        if not currency:
                            logger.debug(f"[bhd_tc] Skipping row (no currency): {row}")
                            continue

                        currency_data[currency].append([
                            row[0], row[1], row[2], row[3] if len(row) > 3 else "", currency, outflow, inflow
                        ])

        if not currency_data:
            logger.warning(f"[bhd_tc] No transaction data extracted from {self.input_file}. "
                           "Trying full text extraction as last resort...")
            # Last resort: extract all text from all pages
            with pdfplumber.open(self.input_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        rows = self._parse_text_lines(text, amount_pattern)
                        for parsed_row in rows:
                            currency_data[parsed_row[4]].append(parsed_row)

        if not currency_data:
            logger.warning(f"[bhd_tc] Still no data found in {self.input_file}. "
                           "The PDF format may have changed.")
            return

        for currency, rows in currency_data.items():
            if not currency or currency.strip() == "":
                logger.warning(f"[bhd_converter] Skipped empty currency in {self.input_file}")
                continue

            output_file = os.path.join(
                self.output_dir, f"{base_name_lower}_{currency.lower()}.csv"
            )
            logger.info(f"[bhd_tc] Writing {len(rows)} row(s) to {output_file} for currency: {currency}")

            with open(output_file, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(self.headers)
                writer.writerows(rows)

        logger.info(f"[bhd_converter] {self.input_file} → multiple CSVs")

    @staticmethod
    def _parse_text_lines(text, amount_pattern):
        """Fallback parser: extract transactions from raw text lines."""
        rows = []
        date_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Look for lines containing a date and a currency amount
            date_match = date_pattern.search(line)
            amount_match = amount_pattern.search(line)
            if date_match and amount_match:
                currency = amount_match.group(1)
                amount_str = amount_match.group(2).replace(",", "")
                date = date_match.group(1)
                # Remove the date and amount from the line to get the memo
                memo = line
                memo = date_pattern.sub('', memo)
                memo = amount_pattern.sub('', memo)
                memo = re.sub(r'\$\s*', '', memo).strip()
                # Clean up extra spaces
                memo = re.sub(r'\s{2,}', ' ', memo).strip()

                # Determine if this is an outflow or inflow
                # Typically credits/payments contain keywords
                inflow_keywords = ['pago', 'abono', 'credito', 'crédito', 'devolucion', 'devolución']
                is_inflow = any(kw in memo.lower() for kw in inflow_keywords)

                outflow = "" if is_inflow else amount_str
                inflow = amount_str if is_inflow else ""

                rows.append(["", date, "", memo, currency, outflow, inflow])
        return rows


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
