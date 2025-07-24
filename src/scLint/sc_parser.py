from pathlib import Path
import sys
from scLint.sc_parser_utility import (
    pool_files,
    id_files,
    open_files,
    create_anndata,
    anndata_out,
)

from scLint.logging_messages import (
    activate,
    log_file_handling,
    caught_file_ext,
    bad_file,
)


class scParser:
    def __init__(
        self,
        path: str,
        sep: str,
        logging: bool = False,
        save_data: bool = False,
        fname: str = None,
    ) -> None:
        # assert input types
        assert isinstance(path, str), f"path must be a str, got {type(path).__name__}"
        assert isinstance(sep, str), f"sep must be a str, got {type(sep).__name__}"
        assert isinstance(
            logging, bool
        ), f"logging must be a bool, got {type(logging).__name__}"
        assert isinstance(
            save_data, bool
        ), f"save_data must be a bool, got {type(save_data).__name__}"
        assert fname is None or isinstance(
            fname, str
        ), f"fname must be a str or None, got {type(fname).__name__}"

        self.path = path
        self.sep = sep
        self.save_data = save_data
        self.fname = fname
        self.sorted = None
        self.df_paths = None
        self.df_dicts = None
        self.adata = None
        if logging:
            activate()

    def path_check(self) -> None:
        """
        This function ensures the path given is valid.
        """
        pathway = Path(self.path)
        check_presence = pathway.exists()
        if not check_presence:
            bad_file(pathway)
            sys.exit()
        check_state = pathway.is_dir()
        if not check_state:
            caught_file_ext()
            sys.exit()
        # NOTE the True argument is a legacy/conceptual argument
        # the intent is that this tool can be used for a directory of
        # files and a small handful that can be based through CLI manually
        log_file_handling(self.path, True)

    def sort_files(self) -> None:
        """
        All files are pooled from the given directory.
        """
        self.sorted = pool_files(self.path)

    def sort_content(self) -> None:
        """
        Files are sorted based on
        nomencalture to the appropriate AnnData attribute.
        """
        self.df_paths = id_files(self.sorted)

    def open_content(self) -> None:
        """
        Files are opened up and modified based
        on memory managementneeds.
        """
        self.dict_dfs = open_files(self.df_paths, sep=self.sep)

    def gen_anndata(self) -> None:
        """
        AnnData Object is generated.
        """
        self.adata = create_anndata(self.dict_dfs)

    def jar_anndata(self) -> None:
        """
        If used the AnnData Object is stored
        in a h5ad file for easy sharing
        """
        if self.save_data:
            anndata_out(self.adata, self.fname)

    def out_anndata(self) -> None:
        """
        Returns the AnnData Object
        """
        return self.adata
