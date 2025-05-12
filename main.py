import os
from converters.banco_popular_dom_converter import convert_bpd_file_to_csv

SOURCE_DIR = 'data'
RESULT_DIR = 'result'

def ensure_result_dir():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)


def clear_result_dir():
    if os.path.exists(RESULT_DIR):
        for filename in os.listdir(RESULT_DIR):
            file_path = os.path.join(RESULT_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print(f"[cleanup] Cleared all files in '{RESULT_DIR}'")


def process_files():
    for filename in os.listdir(SOURCE_DIR):
        file_path = os.path.join(SOURCE_DIR, filename)
        if not os.path.isfile(file_path):
            continue

        name, ext = os.path.splitext(filename.lower())

        if ext == '.txt':
            # at the moment the script assumes that .txt files are only from banco popular
            convert_bpd_file_to_csv(file_path, RESULT_DIR)
        # elif ext == '.xlsx':
        #     convert_excel_to_csv(file_path, RESULT_DIR)
        else:
            print(f"[skip] Unsupported file type: {filename}")

if __name__ == '__main__':
    ensure_result_dir()
    clear_result_dir()
    process_files()
