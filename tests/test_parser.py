import pytest
#temporary line to be replaced once the package is properally installed
from tests.parser_answers import ROOT_DIR, pool_files_ans, id_files_ans
import sys
sys.path.insert(1, '/Users/tanvirsaini/Documents/oacb/scLint/src/scLint/')
from sc_parser_utility import pool_files, id_files, open_files, create_anndata

@pytest.fixture
def pooled_files():
    return pool_files_ans

@pytest.fixture
def identified_files():
    return id_files_ans

@pytest.fixture
def sorted_files():
    return 

def test_pool_files(pooled_files):
    results =  pool_files(ROOT_DIR)
    assert results == pooled_files

def test_id_files(pooled_files, identified_files):
    id_files_ans = id_files(pooled_files)
    assert id_files_ans == identified_files

def test_open_files():
    """TODO"""

def test_anndata():
    """TODO"""
