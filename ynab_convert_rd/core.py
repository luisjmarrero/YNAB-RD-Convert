import os
import logging
import colorlog
from converters.bpd_converter import BPDFileProcessor
from converters.bhd_converter import BHDFileProcessor
from converters.ynab_converter import YNABFileProcessor

DEFAULT_SOURCE_DIR = 'data'
DEFAULT_RESULT_DIR = 'result'

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

def ensure_result_dir(result_dir):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

def clear_result_dir(result_dir):
    if os.path.exists(result_dir):
        for filename in os.listdir(result_dir):
            file_path = os.path.join(result_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        logger.info(f"Cleared all files in '{result_dir}'")

def process_files(source_dir, result_dir):
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if not os.path.isfile(file_path):
            continue
        name, ext = os.path.splitext(filename.lower())
        if ext == '.txt':
            if name.startswith('bpd'):
                logger.info(f"[bpd] Processing file: {file_path}")
                BPDFileProcessor.convert_file(file_path, result_dir)
            else:
                logger.warning(f"[skip txt] Unsupported file prefix: {filename}")
        elif ext == '.pdf':
            if name.startswith('bhd'):
                logger.info(f"[bhd] Processing file: {file_path}")
                BHDFileProcessor.convert_file(file_path, result_dir)
            else:
                logger.warning(f"[skip bhd] Unsupported file prefix: {filename}")
        else:
            logger.warning(f"[skip] Unsupported file type: {filename}")

def run_ynab_converter(result_dir):
    ynab_dir = os.path.join(result_dir, 'ynab')
    logger.info("[ynab] Starting YNAB conversion...")
    YNABFileProcessor.detect_and_convert_all(result_dir, ynab_dir)
    logger.info("[ynab] YNAB conversion completed.")

def run_all(source_dir=DEFAULT_SOURCE_DIR, result_dir=DEFAULT_RESULT_DIR):
    ensure_result_dir(result_dir)
    clear_result_dir(result_dir)
    process_files(source_dir, result_dir)
    run_ynab_converter(result_dir)
