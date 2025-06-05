import pytest
#temporary line to be replaced once the package is properally installed
from parser_answers import ROOT_DICT, pool_files_ans
import sys
sys.path.insert(1, '/Users/tanvirsaini/Documents/oacb/scLint/src/scLint')
from sc_parser_utility import pool_files, id_files, id_files_ans

def test_pool_files():
    results =  pool_files(ROOT_DICT)
    assert results == pool_files_ans

def test_id_files():
    files = pool_files_ans
    assert id_files(files) == id_files_ans

