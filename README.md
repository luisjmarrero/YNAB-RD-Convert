# YNAB RD Convert Tool

Convert your bank transaction files into **YNAB-compatible CSVs** effortlessly. This tool processes files from various Dominican Republic banks and formats them for seamless import into [You Need A Budget (YNAB)](https://www.youneedabudget.com/).

---

## Supported Banks

- **BHD Bank**  
  - Account statements (`bhd_{name}_acc.pdf`)  
  - Credit card statements (`bhd_{name}tc.pdf`)  
  - Ensures positive inflows/outflows and cleans data for YNAB.

- **BPD (Banco Popular)**  
  - Account statements (`bpd_{name}_acc.txt`)  
  - Credit card statements (`bpd_{name}tc.txt`)  
  - Maps transaction types (DB/CR) correctly, adds current year to dates, and formats numbers.



## CLI Usage

After installation, use the CLI tool to convert your bank files:

### Basic usage

```bash
ynab-convert-rd
```

This will process all supported files in the default `data/` folder and output results to the `result/` folder.

### Specify source and result folders

```bash
ynab-convert-rd --source path/to/source --result path/to/result
```

#### Options

- `--source`, `-s`: Path to the folder containing your bank files. Default: `data/`
- `--result`, `-r`: Path to the folder where converted files will be saved. Default: `result/`

### Example

```bash
ynab-convert-rd --source data --result result
```

### Run directly with Python

```bash
python main.py --source data --result result
```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. Place your bank files in the `data/` directory, following these naming conventions:

   - BHD account: `bhd_{your_name}_acc.pdf`  
   - BHD credit card: `bhd_{your_name}tc.pdf`  
   - BPD account: `bpd_{your_name}_acc.txt`  
   - BPD credit card: `bpd_{your_name}tc.txt`

2. Run the converter:  
   ```bash
   python main.py
   ```

3. Your YNAB-ready CSV files will appear in the `result/ynab/` folder, with `_ynab` appended to the original filenames.

---

## Managing Output Data

- If you want to clear it manually, use the helper scripts:  
  ```bash
  ./bin/clear_result.sh
  ```  
  To clear the raw input data folder:  
  ```bash
  ./bin/clear_data.sh
  ```

---

## Installation

### Prerequisites

- Python 3.7 or newer
- (Recommended) Use a virtual environment

### Steps

1. Clone the repository:
2. (Optional) Create and activate a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  ```
3. Install the CLI tool:
  ```bash
  pip install .
  ```

After installation, the command `ynab-convert-rd` will be available globally.