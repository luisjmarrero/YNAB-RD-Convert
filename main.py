import os
from converters.banco_popular_dom_converter import convert_bpd_file_to_csv
from converters.bhd_converter import convert_bhd_file_to_csv

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
            if name.startswith('bpd'):
                print(f"[bpd] Processing file: {file_path}")
                convert_bpd_file_to_csv(file_path, RESULT_DIR)
            # elif name.startswith('bhd'):
            #     convert_excel_to_csv(file_path, RESULT_DIR)
            else:
                print(f"[skip txt] Unsupported file prefix: {filename}")

        elif ext == '.pdf':
            if name.startswith('bhd'):
                print(f"[bhd] Processing file: {file_path}")
                convert_bhd_file_to_csv(file_path, RESULT_DIR)
            else:
                print(f"[skip bhd] Unsupported file prefix: {filename}")
        else:
            print(f"[skip] Unsupported file type: {filename}")


if __name__ == '__main__':
    ensure_result_dir()
    clear_result_dir()
    process_files()
