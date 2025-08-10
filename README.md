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


---

## Installation

1. Clone the repo:  
   ```bash
   git clone https://github.com/yourusername/ynab-rd-convert-tool.git
   cd ynab-rd-convert-tool
   ```

2. (Optional) Create and activate a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
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

- The `result/` folder is **automatically cleared** each time you run the script to avoid mixing old and new data.

- If you want to clear it manually, use the helper scripts:  
  ```bash
  ./bin/clear_result.sh
  ```  
  To clear the raw input data folder:  
  ```bash
  ./bin/clear_data.sh
  ```

---

## Contributing

Feel free to submit issues or PRs for new bank formats or improvements.

---

## License

MIT License — do whatever you want, just don’t blame me.