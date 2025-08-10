import os
import logging
import colorlog
from converters.bpd_converter import BPDFileProcessor
from converters.bhd_converter import BHDFileProcessor
from converters.ynab_converter import YNABFileProcessor

SOURCE_DIR = 'data'
RESULT_DIR = 'result'

# Configure logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s[%(levelname)s]%(reset)s %(message)s',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def ensure_result_dir():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)


def clear_result_dir():
    if os.path.exists(RESULT_DIR):
        for filename in os.listdir(RESULT_DIR):
            file_path = os.path.join(RESULT_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        logger.info(f"Cleared all files in '{RESULT_DIR}'")


def process_files():
    for filename in os.listdir(SOURCE_DIR):
        file_path = os.path.join(SOURCE_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        name, ext = os.path.splitext(filename.lower())

        if ext == '.txt':
            if name.startswith('bpd'):
                logger.info(f"[bpd] Processing file: {file_path}")
                BPDFileProcessor.convert_file(file_path, RESULT_DIR)
            else:
                logger.warning(f"[skip txt] Unsupported file prefix: {filename}")

        elif ext == '.pdf':
            if name.startswith('bhd'):
                logger.info(f"[bhd] Processing file: {file_path}")
                BHDFileProcessor.convert_file(file_path, RESULT_DIR)
            else:
                logger.warning(f"[skip bhd] Unsupported file prefix: {filename}")
        else:
            logger.warning(f"[skip] Unsupported file type: {filename}")


def run_ynab_converter():
    logger.info("[ynab] Starting YNAB conversion...")
    YNABFileProcessor.detect_and_convert_all(RESULT_DIR, os.path.join(RESULT_DIR, 'ynab'))
    logger.info("[ynab] YNAB conversion completed.")


def run_all():
    ensure_result_dir()
    clear_result_dir()
    process_files()
    run_ynab_converter()


if __name__ == '__main__':
    run_all()
