import os
import sys
import argparse
import hdf5plugin
import scanpy as sc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from scLint.utils.logger import Logger, Issue
from scLint.utils.config_loader import get_config

# Using Tevino dataset as first test case
##############################
# Global Vars and Classes
##############################

DEFAULT_OBS_KEYS = [v for v in get_config("obs.keys").values() if v is not None]
DEFAULT_VAR_KEYS = [v for v in get_config("var.keys").values() if v is not None]

##############################
# Linting Rules
##############################


def check_obs(adata, logger, required_keys=None):
    """
    Check that required keys exist in `adata.obs` and that there are no missing values.

    Parameters:
        adata (AnnData): Annotated data object to inspect.
        logger (Logger): Logger instance to record issues.
        required_keys (list, optional): List of keys that must exist in `adata.obs`.
                                        Defaults to standard `DEFAULT_OBS_KEYS`.

    Records:
        - ERROR if a required key is missing.
        - WARNING if missing (NaN) values are found in `adata.obs`.
    """
    if required_keys is None:
        required_keys = DEFAULT_OBS_KEYS

    for key in required_keys:
        if key not in adata.obs.columns:
            logger.record_issue(
                Issue(
                    f"Missing '{key}' in adata.obs",
                    severity="ERROR",
                    source="check_obs",
                )
            )

    if adata.obs.isnull().any().any():
        logger.record_issue(
            Issue("Missing values in adata.obs", severity="WARNING", source="check_obs")
        )


def check_vars(adata, logger, required_keys=None):
    """
    Check that required keys exist in `adata.var` and that variable names are unique.

    Parameters:
        adata (AnnData): Annotated data object to inspect.
        logger (Logger): Logger instance to record issues.
        required_keys (list, optional): List of keys that must exist in `adata.var`.
                                        Defaults to standard `DEFAULT_VAR_KEYS`.

    Records:
        - ERROR if a required key is missing.
        - WARNING if duplicate variable (gene) indices exist.
    """
    if required_keys is None:
        required_keys = DEFAULT_VAR_KEYS

    for key in required_keys:
        if key not in adata.var.columns:
            logger.record_issue(
                Issue(
                    f"Missing '{key}' in adata.var",
                    severity="ERROR",
                    source="check_vars",
                )
            )

    if adata.var.index.duplicated().any():
        logger.record_issue(
            Issue(
                "Duplicate gene indices in adata.var",
                severity="WARNING",
                source="check_vars",
            )
        )


def check_integrity(adata, logger):
    """
    Check consistency between adata.X, adata.obs, and adata.var.

    Returns:
        List[Issue]: Issues found related to matrix shape mismatches.
    """
    if adata.X.shape[0] != adata.obs.shape[0]:
        logger.record_issue(
            Issue(
                message="Mismatch between number of observations and rows in .X",
                severity="ERROR",
                source="check_integrity",
            )
        )
    if adata.X.shape[1] != adata.var.shape[0]:
        logger.record_issue(
            Issue(
                message="Mismatch between number of variables and columns in .X",
                severity="ERROR",
                source="check_integrity",
            )
        )


##############################
# Core Linter Logic
##############################


def run_linter(adata, logger):
    """
    Run a series of linting checks on an AnnData object.

    Parameters:
        adata (AnnData): The annotated data object to lint.

    Returns:
        List[Issue]: A list of Issue objects found during checks.
    """
    rules = [check_obs, check_vars, check_integrity]
    for rule in rules:
        try:
            rule(adata, logger)
        except Exception as e:
            logger.record_issue(Issue(str(e), severity="ERROR", source=rule.__name__))


def print_report(issues, logger=None):
    """
    Output a formatted linting report using the provided logger.

    Parameters:
        issues (List[Issue]): List of Issue instances to display.
        logger (Logger, optional): Logger instance to handle output.
                                   If None, a default verbose logger is used.
    """
    if logger is None:
        logger = Logger(verbose=True)

    if not issues:
        logger.log("No issues found in AnnData object.", severity="INFO")
        return

    errors = sum(1 for i in issues if i.is_error())
    warnings = sum(1 for i in issues if i.is_warning())

    logger.log(f" Linting complete: {len(issues)} issue(s) found", severity="INFO")
    logger.log(f"   {errors} error(s)", severity="INFO")
    logger.log(f"   {warnings} warning(s)\n", severity="INFO")

    for issue in issues:
        logger.record_issue(issue)


def save_plot(func, file_path, *args, **kwargs):
    """
    Save a Scanpy plot to disk with consistent styling and tight layout.

    Parameters:
        func (callable): Scanpy plotting function (e.g., `sc.pl.violin`).
        file_path (str): Destination path for the saved figure.
        *args: Positional arguments passed to the plotting function.
        **kwargs: Keyword arguments passed to the plotting function.
    """
    with plt.rc_context():
        func(*args, show=False, **kwargs)
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()


def basic_exploration(adata, output_dir=None):
    """
    Perform basic exploratory data analysis on an AnnData object.

    This includes:
        - Summary of `adata.obs` and `adata.var`
        - QC metric calculation
        - Violin and scatter plots for QC metrics
        - Identification of highly variable genes (HVGs)
        - PCA computation and visualization

    Parameters:
        adata (AnnData): Annotated data object to explore.
        output_dir (str, optional): If specified, saves plots to this directory as PNGs.
                                    Otherwise, displays plots interactively.
    """
    print(adata)
    print("\nObs columns:", adata.obs.columns.tolist())
    print("Var columns:", adata.var.columns.tolist())

    # Calculate QC metrics
    sc.pp.calculate_qc_metrics(adata, percent_top=[1, 3, 5], inplace=True)

    # Print summary stats
    print("\nQC Summary:")
    ## Added try and except to handle the lack of the columns from erroring out
    try:
        print(adata.obs[["RNA.Counts", "RNA.Features", "Percent.MT"]].describe())
    except:
        print(adata.obs.describe())
    # Plotting
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        ## TODO ADD SOMETHING EXTRA TO DEDUCE THE COLUMNS TO PLOT!!!
        ## ['NAME', 'Cell_line', 'Pool_ID', 'Cancer_type', 'Genes_expressed',
        ##'Discrete_cluster_minpts5_eps1.8', 'Discrete_cluster_minpts5_eps1.5',
        ## 'Discrete_cluster_minpts5_eps1.2', 'CNA_subclone', 'SkinPig_score',
        ##'EMTI_score', 'EMTII_score', 'EMTIII_score', 'IFNResp_score',
        ##'p53Sen_score', 'EpiSen_score', 'StressResp_score', 'ProtMatu_score',
        ##'ProtDegra_score', 'G1/S_score', 'G2/M_score'],
        save_plot(
            sc.pl.violin,
            os.path.join(output_dir, "violin_qc.png"),
            adata,
            ["Cancer_type", "p53Sen_score", "EMTI_score"],
            jitter=0.4,
            multi_panel=True,
        )

        # save_plot(
        #     sc.pl.scatter,
        #     os.path.join(output_dir, "scatter_counts_vs_mt.png"),
        #     adata,
        #     x="Cancer_types",
        #     y="EMTI_score",
        # )

        save_plot(
            sc.pl.scatter,
            os.path.join(output_dir, "scatter_counts_vs_features.png"),
            adata,
            x="p53Sen_score",
            y="Cancer_type",
        )
    else:
        sc.pl.violin(
            adata,
            ["Cancer_type", "p53Sen_score", "EMTI_score"],
            jitter=0.4,
            multi_panel=True,
        )
        sc.pl.scatter(adata, x="p53Sen_score", y="EMTI_score")
        sc.pl.scatter(adata, x="p53Sen_score", y="Cancer_type")

    # HVGs
    # sc.pp.highly_variable_genes(adata, flavor="seurat", n_top_genes=2000)

    # if output_dir:
    #     save_plot(
    #         sc.pl.highly_variable_genes,
    #         os.path.join(output_dir, "highly_variable_genes.png"),
    #         adata,
    #     )
    # else:
    #     sc.pl.highly_variable_genes(adata)

    # PCA
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.pca(adata)

    if output_dir:
        save_plot(
            sc.pl.pca, os.path.join(output_dir, "pca.png"), adata, color="Cancer_type"
        )
    else:
        sc.pl.pca(adata, color="Cancer_type")


def main():
    """
    Command-line interface for running exploratory analysis and linting on an AnnData file.

    Loads the .h5ad file, runs basic QC and visualization routines, performs linting checks,
    and optionally saves plots and logs.

    CLI Arguments:
        adata_path (str): Path to .h5ad file.
        --output_dir (str): Optional directory to save plots instead of displaying them.
        --log_file (str): Optional log file to save linting output.

    Exits with status 1 if linting errors are found.
    """
    parser = argparse.ArgumentParser(
        description="Exploratory analysis of an AnnData object."
    )
    parser.add_argument("adata_path", type=str, help="Path to .h5ad file")
    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="If provided, plots will be saved there as PNGs instead of shown",
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default=None,
        help="Optional path to save log output to a file",
    )
    args = parser.parse_args()

    # Initialize logger
    logger = Logger(verbose=True, log_file=args.log_file)

    logger.log(
        f"Loading AnnData from: {args.adata_path}", severity="INFO", source="main"
    )
    # ===========
    try:
        adata = sc.read_h5ad(args.adata_path)
    except Exception as e:
        logger.log(f"Failed to load AnnData: {e}", severity="ERROR", source="main")
        return

    # Run exploratory analysis and linting
    basic_exploration(adata, output_dir=args.output_dir)

    issues = run_linter(adata, logger)
    print_report(issues, logger)

    # Optionally exit with error if linting failed
    if logger.has_errors():
        logger.log(
            "Exiting with error status due to linting errors.",
            severity="ERROR",
            source="main",
        )
        exit(1)


if __name__ == "__main__":
    main()
