import pytest
import numpy as np
import pandas as pd
import scanpy as sc

from scLint.linter import (
    check_obs,
    check_vars,
    check_integrity,
    run_linter
)
from scLint.utils.logger import Logger, Issue

@pytest.fixture
def valid_adata():
    obs_data = pd.DataFrame({
        "cell_type": ["T", "B"],
        "sample": ["S1", "S2"],
        "batch": ["B1", "B2"],
        "n_genes": [1000, 900],
        "n_counts": [10000, 11000],
        "percent_mito": [5.1, 4.9],
        "leiden": ["0", "1"],
        "condition": ["treated", "control"]
    }, index=["cell1", "cell2"])

    var_data = pd.DataFrame({
        "gene_ids": ["ENSG1", "ENSG2"],
        "gene_symbols": ["TP53", "EGFR"],
        "highly_variable": [True, False],
        "means": [0.5, 0.8],
        "dispersions": [0.1, 0.2],
        "mito": [False, True],
        "chromosome": ["1", "MT"]
    }, index=["gene1", "gene2"])

    X = np.array([[1, 2], [3, 4]])
    return sc.AnnData(X=X, obs=obs_data, var=var_data)


@pytest.fixture
def test_logger():
    return Logger(verbose=False)


def test_check_obs_valid(valid_adata, test_logger):
    check_obs(valid_adata, logger=test_logger)
    assert test_logger.issues == []


def test_check_obs_missing_key(valid_adata, test_logger):
    valid_adata.obs.drop(columns=["cell_type"], inplace=True)
    check_obs(valid_adata, logger=test_logger)
    assert any(i.message.startswith("Missing 'cell_type'") for i in test_logger.issues)
    assert all(isinstance(i, Issue) for i in test_logger.issues)


def test_check_obs_missing_values(valid_adata, test_logger):
    valid_adata.obs.loc["cell1", "sample"] = np.nan
    check_obs(valid_adata, logger=test_logger)
    assert any(i.is_warning() for i in test_logger.issues)


def test_check_vars_valid(valid_adata, test_logger):
    check_vars(valid_adata, logger=test_logger)
    assert test_logger.issues == []


def test_check_vars_missing_key(valid_adata, test_logger):
    valid_adata.var.drop(columns=["gene_ids"], inplace=True)
    check_vars(valid_adata, logger=test_logger) # type: ignore
    assert any(i.message.startswith("Missing 'gene_ids'") for i in test_logger.issues)


def test_check_vars_duplicate_index(valid_adata, test_logger):
    valid_adata.var.index = ["gene1", "gene1"]
    check_vars(valid_adata, logger=test_logger)
    assert any(i.is_warning() for i in test_logger.issues)


def test_check_integrity_valid(valid_adata, test_logger):
    check_integrity(valid_adata, logger=test_logger)
    assert test_logger.issues == []


def test_check_integrity_obs_mismatch(valid_adata, test_logger):
    valid_adata._inplace_subset_var([0])  # Keep 1 var, but 2 obs
    check_integrity(valid_adata, logger=test_logger)
    assert any("Mismatch between number of variables" in i.message for i in test_logger.issues)


def test_check_integrity_var_mismatch(valid_adata, test_logger):
    valid_adata._inplace_subset_obs([0])  # Keep 1 obs, but 2 vars
    check_integrity(valid_adata, logger=test_logger)
    assert any("Mismatch between number of observations" in i.message for i in test_logger.issues)


def test_run_linter_with_known_issues(valid_adata, test_logger):
    valid_adata.obs.drop(columns=["cell_type"], inplace=True)
    run_linter(valid_adata, logger=test_logger)
    assert any(i.is_error() for i in test_logger.issues)


def test_issue_class_str_and_flags():
    issue = Issue("Something broke", severity="ERROR", source="test_rule")
    assert str(issue) == "[ERROR] (test_rule) Something broke"
    assert issue.is_error()
    assert not issue.is_warning()

    warning = Issue("Be cautious", severity="WARNING", source="warn_rule")
    assert str(warning) == "[WARNING] (warn_rule) Be cautious"
    assert not warning.is_error()
    assert warning.is_warning()