from pathlib import Path
import pandas as pd
from scipy import sparse
import file_ext
import logging_messages
import anndata as ad
import hdf5plugin
import numpy as np

FILE_EXT = file_ext.FILE_EXTS

def pool_files(path:str)->dict:
    """
    Input: path to a directory with files
    Output: dict witt with dict name (key)
    with a list of files (values)
    """
    path_object = Path(path)
    path_entries = [entry for entry in path_object.iterdir() if entry.is_file() if entry.name != '.DS_Store']
    path_dict = {'dir':path_object, 'files':path_entries}
    return path_dict

# IT might be better to for go this and have the users input
# all of the files they want to run or create an input template that
# can be read instead. The second step seems like a good idea. maybe
# we can attempt to run the automatted path but if an error occurs we can
# ask for the metadata.
def id_files(path_dict:dict)->dict:
    """
    This function takes in a dictionary and sorts the file paths
    from the input dictionary on what their corresponding AnnData
    entry points are
    """
    # TODO consider using default dict and regex
    # to simplify and scale file identification
    # biggest weak point is obs potentially
    # an assumption is made that all the files in
    # obs will be mergable with each other.
    identified_files = {}
    identified_files['uns'] = []
    for file_path in path_dict['files']:
        name = Path(file_path).name  # safer than str(file_path)
        if "_spliced_counts" in name:
            identified_files["spliced"] = file_path
        elif "_unspliced_counts" in name:
            identified_files["unspliced"] = file_path
        elif "_counts" in name and not "_spliced_counts" in name and not "_unspliced_counts" in name:
            identified_files['X'] = file_path
        elif "cell_metadata" in name:
            identified_files['obs'] = file_path
        elif "gene_metadata" in name:
            identified_files['var'] = file_path
        else:
            identified_files['uns'].append(file_path)
    return identified_files

def open_files(identified_files:dict, sep='\t'):
    """
    Input: A dict with identified files and their paths
    Output: dict with pandas DataFrames.
    """
    file_keys = identified_files.keys()
    for_anndata = {}
    for file_key in file_keys:
        # TODO potentially move just the uns into a 
        # a python so that way the code is a bit more
        # readable later on.
        file_paths = identified_files[file_key]
        if file_key == 'uns':
            logging_messages.opening_file(file_key, file_list=file_paths)
            if len(file_paths) == 1:
                opened_files = pd.read_csv(file_paths[0], sep=sep, index_col=0)
            else:
                opened_files = [pd.read_csv(file_path, sep=sep, index_col=0) for 
                                        file_path in file_paths
                                        ]
            for_anndata['uns'] = opened_files
            continue
        # End logic adjustments for 'uns' data.
        logging_messages.opening_file(file_key, file_name=file_paths)
        # TODO encapsulate logic in the future
        # this is being done to allow complete control over the data handeling
        # versus using scanpay's sc.read_csv
        df = pd.read_csv(file_paths, sep=sep, index_col=0)
        if file_key in ['X','spliced_counts', 'unspliced_counts']:
            df = sparse.csr_matrix(df.values, dtype=np.float32)
        for_anndata[file_key] = df
    return for_anndata

def _anndata_helper(adata:ad.AnnData, data_type:str, data:pd.DataFrame) -> ad.AnnData:
    """
    AnnData helper function that helps dictate where the data
    should be assigned to.

    Input: AnnData Object, string addressing data type, pandas dataframe
    """
    # NOTE: Most raw count files (like from velocyto, loom, or Cell Ranger) store data as genes (rows) × cells (columns).
    # TODO: Might want to set up a step where we check the dim of the data. easiest logic: ensure rows < columns.
    try:
        match data_type:
            case 'obs':
                adata.obs = data
            case 'var':
                adata.var = data
            # TODO fix this and ensure the aforementioneg logic is used
            # instead of this before next deployment.
            case 'spliced':
                adata.layers['spliced'] = data.T
            case 'unspliced':
                adata.layers['unspliced'] = data.T
            case 'uns':
                for data_entry in data:
                    layer_value = len(adata.uns)
                    layer_name = f"layer_{layer_value}"
                    adata.uns[layer_name] = data_entry
            # TODO things that are left to manage -
            # adata.obsm, adata.varm, adata.uns, adata.raw	
            # and if it’s cell-level (per row) then adata.obs["batch"] is needed
            # or if it’s global (e.g., sample-level, run config) then adata.uns["metadata"]
            # is needed
            case _:
                #TODO WARNING AND RETURN 1
                pass
    except ValueError as ve:
        # TODO this needs to be fctored in such a way where
        # infinitely many unstructured data layers can be added
        # idea:: helper function that checks the current state of uns
        # and then adds additional uns layers?
        error_name = type(ve).__name__
        alt_action = f'Storing data into "uns" instead of {data_type}'
        #logging_messages.error(data_type,error_name, alt_action)
        print(ve)
        layer_value = len(adata.uns)
        layer_name = f"layer_{layer_value}"
        adata.uns[layer_name] = data
    return adata
            

def create_anndata(opened_files:dict, store_disk:bool=False, fname:str='anndata') -> ad.AnnData:
    # TODO move key_priority into a config file
    key_priority = {'X': 0, 'obs': 1, 'var': 2, 'metadata': 3}
    anndata_keys = sorted(opened_files.keys(), key=lambda k: key_priority.get(k, 100))
    for index, adata_key in enumerate(anndata_keys):
        data_df = opened_files[adata_key]
        logging_messages.assign_adata(adata_key)
        if index == 0:
            adata = ad.AnnData(X=data_df.T)
            continue
        adata = _anndata_helper(adata, adata_key, data_df)
    logging_messages.success()
    return adata

def anndata_out(adata:ad.AnnData, fname:str='anndata') -> None:
    fname += '.h5ad'
    logging_messages.save_to_disk('anndata object', fname)
    adata.write_h5ad(fname,compression=hdf5plugin.FILTERS["zstd"])
    logging_messages.success()