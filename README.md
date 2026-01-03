# xls2sepaxml

A web-based tool to convert Excel files (.xlsx, .xls) to **SEPA XML Bulk Transfer** files. 
This tool allows you to convert a list of recipients from an Excel sheet into a single SEPA-compliant XML file that can be uploaded to your online banking portal to execute multiple transfers at once.

It processes data entirely in-memory for better privacy and security.

## Features
- **Bulk Transfers:** Generate a single XML file for multiple payments.
- **Online Banking Ready:** Output format is standard PAIN.001.001.03, compatible with most banks.
- **In-Memory Processing:** No files are stored on the server disk.
- **Data Validation:** Uses `schwifty` for IBAN/BIC validation and `sepaxml` for standardized output.
- **Interactive Preview:** Verify your data mapping before generating the final XML.
- **Easy Installation:** Can be installed as a Python package.

## Installation

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/uzorn/xls2sepaxml.git
   cd xls2sepaxml
   ```
2. Install the package:
   ```bash
   pip install .
   ```

## Usage

After installation, you can start the web interface using the following command:

```bash
xls2sepa-web
```

Then open your browser at: `http://127.0.0.1:5000`

### Workflow:
1. **Upload:** Select and upload your Excel file.
2. **Mapping:** The tool suggests mappings for SEPA fields. Adjust them if necessary and enter your sender details.
3. **Preview:** Review the first few rows of your data.
4. **Download:** Generate and download the `sepa_transfer.xml` file.

## Development

To run the app in development mode:
```bash
python xls2sepaxml/web.py
```

## License
MIT
