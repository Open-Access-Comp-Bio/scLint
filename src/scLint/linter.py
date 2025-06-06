import scanpy as sc
import numpy as np
import pandas as pd

##############################
# Global Vars and Classes
##############################

class Issue:
    def __init__(self, message, severity="ERROR", source=None):
        self.message = message
        self.severity = severity.upper()
        self.source = source

    def __repr__(self):
        return (
            f"Issue(severity='{self.severity}', "
            f"source='{self.source}', message='{self.message}')"
        )

    def __str__(self):
        """
        User-friendly string for display.
        Example: [ERROR] (check_obs): Missing 'cell_type' in adata.obs
        """
        parts = [f"[{self.severity}]"]
        if self.source:
            parts.append(f"({self.source})")
        parts.append(self.message)
        return " ".join(parts)

    def is_error(self):
        return self.severity == "ERROR"

    def is_warning(self):
        return self.severity == "WARNING"


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
        print("✅ No issues found in AnnData object.")
        return

    errors = sum(1 for i in issues if i.is_error())
    warnings = sum(1 for i in issues if i.is_warning())

    print(f" Linting complete: {len(issues)} issue(s) found")
    print(f"   {errors} error(s)")
    print(f"   {warnings} warning(s)\n")

    for issue in issues:
        print(f" - {issue}")
