from sc_parser_utility import (pool_files, id_files, open_files, create_anndata, anndata_out)
import logging_messages
from pathlib import Path
import sys

class scParser():
    def __init__(self, path:str, sep:str, logging:bool=False, save_data:bool = False, fname:str = None)->None:
        self.path = path
        self.sep = sep
        self.save_data = save_data
        self.fname = fname
        self.sorted = None
        self.df_paths = None
        self.df_dicts = None
        self.adata = None
        if logging:
            logging_messages.activate()

    def path_check(self)->None:
        """
        This function ensures the path given 
        """
        pathway = Path(self.path)
        check_presence = pathway.exists()
        if not check_presence:
            logging_messages.s
            sys.exit()
        check_state = pathway.is_dir()
        if not check_state:
            logging_messages.caught_file_ext()
            sys.exit()
        # NOTE the True argument is a legacy/conceptual argument
        # the intent is that this tool can be used for a directory of
        # files and a small handfull that can be based through CLI manually
        logging_messages.log_file_handeling(self.path, True)

    def sort_files(self) -> None:
        self.sorted  =  pool_files(self.path)

    def sort_content(self)->None:
        self.df_paths = id_files(self.sorted)

    def open_content(self)->None:
        self.dict_dfs = open_files(self.df_paths, 
                                   sep=self.sep)

    def gen_anndata(self)->None:
        self.adata = create_anndata(self.dict_dfs)

    def jar_anndata(self):
        if self.save_data:
            anndata_out(self.adata, self.fname)
