import pandas as pd
import anndata as ad
import sc_parser_utility
import logging_messages
import file_ext

class scParser():
    def __init__(self, path:list, is_dir=True):
        self.path = path
        self.is_dir = is_dir
        self.adata = ad.AnnData()

    def path_check(self):
        # TODO remove this function, assert that the input
        # to always be a directory of files.
        if self.is_dir is True and file_ext.FILE_EXTS in self.path.any():
            logging_messages.caught_file_ext()
            self.is_dir=False

    def open_content(self,):
        logging_messages.log_file_messages(self.path, self.is_dir)
        sc_parser_utility.id_files(self.path)
        pass

    def clean_matrix_data():
        pass

    def gen_anndata():
        pass

    def jar_anndata():
        pass