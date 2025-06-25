<img src="assets/scLint.png" alt="scLint logo" width="600"/>

# scLint

Python tool for linting, cleaning, and producing exploratory analysis of single-cell RNA-seq data.

## Preparing Environment

If you haven't done so already, you can download the `environment.yml` file and run the following command below:


```bash
conda env create -f environment.yml
```

This command only needs to run once, and it will install:
- Python
- Pandas
- Numpy
- Scipy
- Jupyter notebook toolings

## Activate Environment

Make sure you have Conda installed. Then run:

```bash
conda activate sclint
```
---
## Features

- Accepts a directory of scRNA-seq count data, metadata, and QC files
- Converts inputs into a structured `AnnData` object
- Supports flexible delimiter input (`tab` or `comma`)
- Optional `.h5ad` file export
- Verbose mode for tracking progress

---

## Directory Requirements

Your input directory should contain:
- Gene-by-cell count matrices (`.tsv` or `.csv`)
- Metadata files for cells and samples
- Optional QC summary or label files

## Usage [WILL NEED TO BE UPDATED AFTER MERGING COMPONENTS!!!]
```
python main.py <dir_path> [--sep <sep>] [--verbose] [--save] [--output <output_file>]
```
## Example Use Cases

### Basic usage (tab-delimited files):
```
python sc_parser.py ./tests/collateral/scdata
```

### Use comma-delimited input:
```
python sc_parser.py ./tests/collateral/scdata --sep comma
```

### Save output to disk within running dir as `my_data.h5ad`:
```
python sc_parser.py ./tests/collateral/scdata --save --output my_data
```

### Save output to disk outside of running dir as 1my_data.h5ad1:
```
python sc_parser.py ./tests/collateral/scdata --save --output \Desired\Dir\to\store\my_data
```

### Full verbose run:
```
python sc_parser.py ./tests/collateral/scdata --sep tab --verbose --save --output result
```

## Notes
- If `--save` is used without `--output`, the file will not be saved.
- The tool currently assumes a specific structure for the input directory; future versions will include validation steps and automatic detection.
