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
- Scanpy
- Scipy
- Jupyter notebook toolings
- Appropriate addons for the above


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

## Usage
### Running the file parser and sorter
```
scLint <dir_path> [--sep <sep>] [--verbose] [--save] [--output <output_file>]
```
### Running data QC
```
# TODO
```
### Running the full pipeline
```
# TODO
```
## Example Use Cases

### Basic usage (tab-delimited files):
```
scLint ./tests/collateral/scdata
```

### Use comma-delimited input:
```
scLint ./tests/collateral/scdata --sep comma
```

### Save output to disk within running dir as `my_data.h5ad`:
```
scLint ./tests/collateral/scdata --save --output my_data
```

### Save output to disk outside of running dir as `my_data.h5ad`:
```
scLint ./tests/collateral/scdata --save --output \Desired\Dir\to\store\my_data
```

### Full verbose run:
```
scLint ./tests/collateral/scdata --sep tab --verbose --save --output result
```

## Notes
- If `--save` is used without `--output`, the file will not be saved.
- The tool currently assumes a specific structure for the input directory; future versions will include validation steps and automatic detection.