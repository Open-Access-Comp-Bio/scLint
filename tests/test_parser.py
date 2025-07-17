import pytest
import pandas as pd
import scipy.sparse as sp
import anndata as ad
from tests.parser_answers import ROOT_DIR, pool_files_ans, id_files_ans
from scLint.sc_parser_utility import pool_files, id_files, open_files, create_anndata


@pytest.fixture
def pooled_files():
    return pool_files_ans


@pytest.fixture
def identified_files():
    return id_files_ans


def test_pool_files(pooled_files):
    results = pool_files(ROOT_DIR)
    assert results["dir"] == pooled_files["dir"]
    assert set(results["files"]) == set(pooled_files["files"])


def test_id_files(pooled_files, identified_files):
    id_files_output = id_files(pooled_files)
    assert id_files_output == identified_files


def test_open_files(identified_files):
    result = open_files(identified_files)
    assert isinstance(result, dict)
    for key, value in result.items():
        if key == "uns":
            assert isinstance(value, list)
        else:
            assert isinstance(value, (pd.DataFrame, sp.spmatrix))


def test_anndata(identified_files):
    opened_files = open_files(identified_files)
    generated_adata = create_anndata(opened_files)
    assert isinstance(generated_adata, ad.AnnData)
