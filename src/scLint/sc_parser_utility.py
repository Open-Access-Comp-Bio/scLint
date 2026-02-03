from pathlib import Path
import pandas as pd
import anndata as ad
import hdf5plugin
import numpy as np
import warnings
from scLint.logging_messages import (
    opening_file,
    assign_adata,
    success,
    save_to_disk,
    error,
    chunk_processing,
    completed_processing,
)
from scLint.utils.config_loader import load_config

warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=pd.errors.DtypeWarning)

CHUNKSIZES = int(load_config()["data.handling"]["CHUNKSIZES"])



def pool_files(path: str) -> dict:
    """
    Input: path to a directory with files
    Output: dict witt with dict name (key)
    with a list of files (values)
    """
    path_object = Path(path)
    path_entries = [
        entry
        for entry in path_object.iterdir()
        if entry.is_file()
        if entry.name != ".DS_Store"
    ]
    path_dict = {"dir": path_object, "files": path_entries}
    return path_dict


# IT might be better to for go this and have the users input
# all of the files they want to run or create an input template that
# can be read instead. The second step seems like a good idea. maybe
# we can attempt to run the automatted path but if an error occurs we can
# ask for the metadata.
def id_files(path_dict: dict) -> dict:
    """
    This function takes in a dictionary and sorts the file paths
    from the input dictionary on what their corresponding AnnData
    entry points are
    """
    # TODO consider using default dict and regex
    # to simplify and scale file identification
    # biggest weak point is obs potentially
    # an assumption is made that all the files in
    # obs will be mergeable with each other.
    identified_files = {}
    identified_files["uns"] = []
    for file_path in path_dict["files"]:
        name = str(Path(file_path).name).lower()  # safer than str(file_path)
        if "_spliced_counts" in name or "_spliced_cpm" in name:
            identified_files["spliced"] = file_path
        elif "_unspliced_counts" in name or "_unspliced_cpm" in name:
            identified_files["unspliced"] = file_path
        elif (
            ("raw" in name or "umi" in name)
            and ("_spliced_counts" not in name)
            and ("_unspliced_counts" not in name)
        ):
            # NOTE + TODO Should we let the user predefine what X is? it reduces the guessing game by a bit, it would be
            # one additional argument, it could be optional instead of mandatory
            # NOTE found from doing additional research on the use of X
            # adata.X simply holds “the matrix you are currently analysing.”
            # Whether that matrix is raw counts or normalised / log-transformed
            # counts is entirely up to how you build the object.
            # NOTE + TODO maybe for our nomenclature we include "initial" in the nomenclature
            identified_files["X"] = file_path
        elif (
            ("normalized_counts" in name or "cpm_" in name)
            and ("spliced" not in name)
            and ("unspliced" not in name)
        ):
            identified_files["normalized"] = file_path
        elif "cell_metadata" in name:
            identified_files["obs"] = file_path
        elif "gene_metadata" in name:
            identified_files["var"] = file_path
        else:
            identified_files["uns"].append(file_path)
    return identified_files


def open_files(identified_files: dict, sep="\t", chunksizes=CHUNKSIZES):
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
        if file_key == "uns":
            opening_file(file_key, file_list=file_paths)
            if len(file_paths) == 1:
                opened_files = pd.read_csv(
                    file_paths[0], sep=sep, index_col=0, dtype=str
                )
            else:
                opened_files = [
                    pd.read_csv(file_path, sep=sep, index_col=0, dtype=str)
                    for file_path in file_paths
                ]
            for_anndata["uns"] = opened_files
            continue
        # End logic adjustments for 'uns' data.
        opening_file(file_key, file_name=file_paths)
        # TODO encapsulate logic in the future
        # this is being done to allow complete control over the data handling
        # versus using scanpay's sc.read_csv
        if file_key in ["X", "spliced_counts", "unspliced_counts", "normalized"]:
            # TODO move to future function and add futuer arguments for chunksize controlling
            # TODO FOLLOW THROUGH WITH CHUNKSIZE BUT DON'T DO SPARSE
            # DEL OLD VARIABLES FOR MEMORY MANAGEMENT AND THEN TRY DO PD CONCAT
            cols_to_rm = {"cell_line", "pool_id", "Cell_line", "Pool_ID"}
            chunk_iterator = pd.read_csv(
                file_paths, sep=sep, chunksize=chunksizes, engine="c", index_col=0
            )
            sparse_chunks = []
            for index, df_chunk in enumerate(chunk_iterator):
                chunk_processing(index)
                df_chunk = df_chunk.T
                cols_to_use = [col for col in df_chunk.columns if col not in cols_to_rm]
                df_chunk = df_chunk[cols_to_use]
                df_chunk = df_chunk.T
                df_chunk = df_chunk.astype(np.float32)
                completed_processing(index)
                # NOTE originally I was using sparse csr matrix to reduce
                # the amoount of memory these dataframes were taking, but it
                # seems like using np.float32 reduces the memory enough?
                # once this is functionalized better we should do a memory
                # comparison test for pd.DataFrame w/ dtypes of np.float32 vs
                # sparse.csr_matrix. Which ever takes up less space in mem should be
                # selected at least that's what I think.
                # df_chunk = sparse.csr_matrix(df_chunk.values)
                sparse_chunks.append(df_chunk)
                del df_chunk
            df = pd.concat(sparse_chunks)
            df = df.T
        else:
            df = pd.read_csv(file_paths, sep=sep, index_col=0, dtype=str)
        for_anndata[file_key] = df
    if "var" not in file_keys:
        # TODO this will also need to be properly
        gene_symbols = for_anndata["X"].columns
        for_anndata["var"] = pd.DataFrame(data=gene_symbols, columns=["gene_symbols"])
    if "obs" not in file_keys:
        cell_ids = for_anndata["X"].index
        for_anndata["obs"] = pd.DataFrame(data=cell_ids, columns=["cell_ids"])
    # NOTE move the next lines of code into a function
    return for_anndata


def dimensionality_check(for_anndata: dict) -> dict:
    # shape returns a tuple of rows x columns
    count_matrix = for_anndata["X"].shape
    # obs counts are rows
    obs_count = for_anndata["obs"].shape
    # var counts are columns
    var_count = for_anndata["var"].shape
    if obs_count != counts_matrix[1]:
        valid_obs = for_anndata["obs"].iloc[:, 0]
        for_anndata["X"] = for_anndata["X"].isin(valid_obs)
    if var_count != counts_matrix[0]:
        valid_vars = for_anndata["var"].iloc[:, 0]
        for_anndata["X"] = for_anndata["X"].loc[
            :, for_anndata["X"].columns.isin(valid_vars)
        ]
    return anndata_dict


def _anndata_helper(
    adata: ad.AnnData, data_type: str, data: pd.DataFrame
) -> ad.AnnData:
    """
    AnnData helper function that helps dictate where the data
    should be assigned to.

    Input: AnnData Object, string addressing data type, pandas dataframe
    """
    # NOTE: Most raw count files (like from velocyto, loom, or Cell Ranger) store data as genes (rows) × cells (columns).
    # TODO: Might want to set up a step where we check the dim of the data. easiest logic: ensure rows < columns.
    try:
        match data_type:
            case "obs":
                # NOTE should this be it's own function?
                # this should probably get a logging message
                data_cols = data.columns
                for data_col in data_cols:
                    try:
                        data[data_col] = data[data_col].astype(float)
                    except ValueError:
                        data[data_col] = data[data_col].astype(str)
                adata.obs = data
            case "var":
                data = data.astype(str)
                adata.var = data
            case "spliced":
                adata.layers["spliced"] = data.T
            case "unspliced":
                adata.layers["unspliced"] = data.T
            case "uns":
                if isinstance(data, list):
                    # TODO THIS SECTION NEEDS TO BE REVISED
                    # if data_entry is used, it causes the pytest
                    # to fail!!!
                    for data_entry in data:
                        layer_value = len(adata.uns)
                        layer_name = f"layer_{layer_value}"
                        adata.uns[layer_name] = data
                else:
                    layer_name = f"layer_0"
                    adata.uns[layer_name] = data
            # TODO things that are left to manage -
            # adata.obsm, adata.varm, adata.uns, adata.raw
            # and if it’s cell-level (per row) then adata.obs["batch"] is needed
            # or if it’s global (e.g., sample-level, run config) then adata.uns["metadata"]
            # is needed
            case _:
                # TODO WARNING AND RETURN 1
                pass
    except ValueError as ve:
        # NOTE determine if this is still an issue, should this be here?
        # TODO this needs to be factored in such a way where
        # infinitely many unstructured data layers can be added
        # idea:: helper function that checks the current state of uns
        # and then adds additional uns layers?
        # NOTE + TODO in a future update we can provide a optional input
        # where the user can have the scLint automatically adjust the obs
        # values based on the sample names that are present in the matrix
        # the dictionary is still present
        error_name = type(ve).__name__
        alt_action = f'Storing data into "uns" instead of {data_type}'
        error(data_type, error_name, ve, issue_handling=alt_action)
        layer_value = len(adata.uns)
        layer_name = f"layer_{layer_value}"
        # NOTE unstructured must be ONE DATA TYPE
        data = data.astype(str)
        adata.uns[layer_name] = data
    return adata


def create_anndata(opened_files: dict) -> ad.AnnData:
    """
    This function creates an AnnData object after the
    dictionary of file paths has the files opened.

    Input
        opened_files: dictionary of data structs, Pd.DataFrame, Sparse Matrix, etc etc...
    Output
        AnnData Object
    """
    # TODO move key_priority into a config file
    key_priority = {"X": 0, "obs": 1, "var": 2, "metadata": 3}
    anndata_keys = sorted(opened_files.keys(), key=lambda k: key_priority.get(k, 100))
    for index, adata_key in enumerate(anndata_keys):
        data_df = opened_files[adata_key]
        assign_adata(adata_key)
        if index == 0:
            adata = ad.AnnData(X=data_df)
            continue
        adata = _anndata_helper(adata, adata_key, data_df)
    success()
    return adata


def anndata_out(adata: ad.AnnData, fname: str = "anndata") -> None:
    """
    This function outputs an AnnData object to a h5ad file.
    The default file name if not provided is anndata.

    Input
        adata: AnnData Object
        fname: optional, default name anndata
    """
    fname += ".h5ad"
    save_to_disk("anndata object", fname)
    adata.write_h5ad(fname, compression=hdf5plugin.FILTERS["zstd"])
    success()
