# Foundation Medicine Parser

[Foundation Medicine][1] is a company that provides comprehensive genomic profiling services for cancer patients. The Foundation Medicine Parser is a Python package that allows users to parse the Foundation Medicine reports and extract the relevant information. The package is designed to work with the Foundation Medicine reports in XML format.

## Installation

The Foundation Medicine Parser can be installed using pip:

```bash
pip install https://github.com/seandavi/foundation-medicine-xml-parser.git
```

## Usage

While the library can be useful by itself, the main entry point for 
most users will be the `process_fmi` command line utility. This utility
will parse the Foundation Medicine XML files in a directory and output
the results of the parsing to an Excel file and a set of CSV files.

```bash
process_fmi --input_dir /path/to/foundation-medicine-xml-files --output_dir /path/to/output
```

The output directory will contain (currently) these files:

```
output_dir
├── assay_and_patient_data.csv
├── biomarkers.csv
├── copy_number_alterations.csv
├── fmi_report.xlsx
├── rearrangements.csv
└── short_variants.csv
```

The CSV files contain the parsed data in a tabular format. The Excel file contains the same data in separate
worksheets.

[1]: https://www.foundationmedicine.com/
