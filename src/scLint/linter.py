import os
import sys
import argparse
import hdf5plugin
import scanpy as sc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.logger import Issue


# Using Tevino dataset as first test case
##############################
# Global Vars and Classes
##############################


DEFAULT_OBS_KEYS = [
    "cell_type", "sample", "batch", "n_genes", "n_counts",
    "percent_mito", "leiden", "condition"
]

DEFAULT_VAR_KEYS = [
    "gene_ids", "gene_symbols", "highly_variable", "means",
    "dispersions", "mito", "chromosome"
]

##############################
# Linting Rules
##############################

def check_obs(adata, required_keys=None):
    if required_keys is None:
        required_keys = DEFAULT_OBS_KEYS

    issues = []
    for key in required_keys:
        if key not in adata.obs.columns:
            issues.append(Issue(f"Missing '{key}' in adata.obs", severity="ERROR", source="check_obs"))

    if adata.obs.isnull().any().any():
        issues.append(Issue("Missing values in adata.obs", severity="WARNING", source="check_obs"))

    return issues


def check_vars(adata, required_keys=None):
    if required_keys is None:
        required_keys = DEFAULT_VAR_KEYS

    issues = []
    for key in required_keys:
        if key not in adata.var.columns:
            issues.append(Issue(f"Missing '{key}' in adata.var", severity="ERROR", source="check_vars"))

    if adata.var.index.duplicated().any():
        issues.append(Issue("Duplicate gene indices in adata.var", severity="WARNING", source="check_vars"))

    return issues


def check_integrity(adata):
    """
    Check consistency between adata.X, adata.obs, and adata.var.

    Returns:
        List[Issue]: Issues found related to matrix shape mismatches.
    """
    issues = []
    if adata.X.shape[0] != adata.obs.shape[0]:
        issues.append(Issue(
            message="Mismatch between number of observations and rows in .X",
            severity="ERROR",
            source="check_integrity"
        ))
    if adata.X.shape[1] != adata.var.shape[0]:
        issues.append(Issue(
            message="Mismatch between number of variables and columns in .X",
            severity="ERROR",
            source="check_integrity"
        ))
    return issues


##############################
# Core Linter Logic
##############################

def run_linter(adata):
    """
    Run a series of linting checks on an AnnData object.

    Parameters:
        adata (AnnData): The annotated data object to lint.

    Returns:
        List[Issue]: A list of Issue objects found during checks.
    """
    rules = [check_obs, check_vars, check_integrity]
    issues = []
    for rule in rules:
        try:
            result = rule(adata)
            issues.extend(result)
        except Exception as e:
            issues.append(Issue(
                message=str(e),
                severity="ERROR",
                source=rule.__name__
            ))
    return issues


def print_report(issues):
    """
    Print a formatted linting report from Issue objects.

    Parameters:
        issues (List[Issue]): List of Issue instances to display.
    """
    if not issues:
        print("No issues found in AnnData object.")
        return

    errors = sum(1 for i in issues if i.is_error())
    warnings = sum(1 for i in issues if i.is_warning())

    print(f" Linting complete: {len(issues)} issue(s) found")
    print(f"   {errors} error(s)")
    print(f"   {warnings} warning(s)\n")

    for issue in issues:
        print(f" - {issue}")


def save_plot(func, file_path, *args, **kwargs):
    """Helper to save Scanpy plots with full control."""
    with plt.rc_context():
        func(*args, show=False, **kwargs)
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()


def basic_exploration(adata, output_dir=None):
    print(adata)
    print("\nObs columns:", adata.obs.columns.tolist())
    print("Var columns:", adata.var.columns.tolist())

    # Calculate QC metrics
    sc.pp.calculate_qc_metrics(adata, percent_top=[1, 3, 5], inplace=True)

    # Print summary stats
    print("\nQC Summary:")
    print(adata.obs[['RNA.Counts', 'RNA.Features', 'Percent.MT']].describe())

    # Plotting
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        save_plot(
            sc.pl.violin,
            os.path.join(output_dir, "violin_qc.png"),
            adata,
            ['RNA.Features', 'RNA.Counts', 'Percent.MT'],
            jitter=0.4,
            multi_panel=True
        )

        save_plot(
            sc.pl.scatter,
            os.path.join(output_dir, "scatter_counts_vs_mt.png"),
            adata,
            x='RNA.Counts',
            y='Percent.MT'
        )

        save_plot(
            sc.pl.scatter,
            os.path.join(output_dir, "scatter_counts_vs_features.png"),
            adata,
            x='RNA.Counts',
            y='RNA.Features'
        )
    else:
        sc.pl.violin(adata, ['RNA.Features', 'RNA.Counts', 'Percent.MT'], jitter=0.4, multi_panel=True)
        sc.pl.scatter(adata, x='RNA.Counts', y='Percent.MT')
        sc.pl.scatter(adata, x='RNA.Counts', y='RNA.Features')

    # HVGs
    sc.pp.highly_variable_genes(adata, flavor="seurat", n_top_genes=2000)

    if output_dir:
        save_plot(
            sc.pl.highly_variable_genes,
            os.path.join(output_dir, "highly_variable_genes.png"),
            adata
        )
    else:
        sc.pl.highly_variable_genes(adata)

    # PCA
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.pca(adata)

    if output_dir:
        save_plot(
            sc.pl.pca,
            os.path.join(output_dir, "pca.png"),
            adata,
            color='RNA.Counts'
        )
    else:
        sc.pl.pca(adata, color='RNA.Counts')

def main():
    parser = argparse.ArgumentParser(description="Exploratory analysis of an AnnData object.")
    parser.add_argument("adata_path", type=str, help="Path to .h5ad file")
    parser.add_argument(
        "--output_dir", type=str, default=None,
        help="If provided, plots will be saved there as PNGs instead of shown"
    )
    args = parser.parse_args()

    # Load data
    print(f"Loading AnnData from: {args.adata_path}")
    adata = sc.read_h5ad(args.adata_path)

    basic_exploration(adata, output_dir=args.output_dir)

if __name__ == "__main__":
    main()