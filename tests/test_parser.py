import pytest
#temporary line to be replaced once the package is properally installed
from parser_answers import ROOT_DICT, pool_files_ans, id_files_ans
import sys
sys.path.insert(1, '/Users/tanvirsaini/Documents/oacb/scLint/src/scLint')
from sc_parser_utility import pool_files, id_files, open_files, create_anndata
import logging_messages


def test_pool_files():
    results =  pool_files(ROOT_DICT)
    assert results == pool_files_ans

def test_id_files():
    files = pool_files_ans
    identified_files = id_files(files)
    assert identified_files == id_files_ans

# TODO Tuesday's goal create a smaller test file
# TODO model pytest after Steve's work
# TODO adjust logging messages to match Steve's works

def test_open_files():
    results = open_files(id_files_ans)
    return(results)

def test_anndata(results):
    my_adata = create_anndata(results,False, '1strun')
    return my_adata

files = pool_files(ROOT_DICT)
print(files)
myids = id_files(files)
print(myids)

logging_messages.activate()
results = test_open_files()
# import pickle
# with open('dataframes.pkl', 'wb') as f:
#     pickle.dump(results, f)
output = test_anndata(results)
print(output)
print(output.X)
print(output.layers)
