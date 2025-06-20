import pandas as pd
import anndata as ad
import sc_parser_utility
import logging_messages
import file_ext

class scParser():
    def __init__(self, path:list, is_dir=True, sep=None, combine=None):
        self.path = path
        #TODO is_dir may not be needed, so remove
        self.is_dir = is_dir
        self.adata = ad.AnnData()
        if sep is None:
            self.sep = '\t'
        else:
            self.sep = sep
        if combine is None:
            self.combine = 'combine'
        else:
            self.combine = combine
        self.sorted = None
        self.df_dicts = None

    def path_check(self)->None:
        # TODO remove this function, assert that the input
        # to always be a directory of files.
        if self.is_dir is True and file_ext.FILE_EXTS in self.path.any():
            logging_messages.caught_file_ext()
            self.is_dir=False

    def sort_content(self)->None:
        # TODO some layer of sophisticated name checking
        # might be needed in the future. i.e. are unsorted
        # and sorted present? is var empty? what to do when
        # var is empty? etc..etc..
        logging_messages.log_file_messages(self.path, self.is_dir)
        self.sorted = sc_parser_utility.id_files(self.path)

    def open_content(self)->None:
        self.dict_dfs = sc_parser_utility.open_files(self.sorted, sep=self.sep, combine=self.combine)

    def gen_anndata()->None:
        #TODO for keys in anndata generate
        #appropriate anndata object
        pass

    def jar_anndata():
        pass