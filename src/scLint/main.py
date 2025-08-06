import argparse
import scanpy as sc
from scLint.sc_parser import scParser
from scLint.linter import run_linter, print_report, basic_exploration
from scLint.utils.logger import Logger, Issue


def arg_parser():
    """
    Custom argument parser using argparse
    Input:
        The only required input is dir_path
    Output
        Outputs the parser object
    """
    parser = argparse.ArgumentParser(
        description="scParser, a tool for sorting scRNA seq files into an AnnData Object and begin exploratory data analysis."
    )
    parser.add_argument(
        "dir_path",
        help="Required. Pathway to directory with scRNA count files, metadata, etc.",
    )
    parser.add_argument(
        "action",
        choices=["parse","lint","full"],
        help="Required. Select to parse data, lint data, or to run the complete pipeline.",
    )
    parser.add_argument(
        "--sep",
        default="tab",
        help="Deliminator/separator used throughout the files within dir_path. Default is tab.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print logging messages."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the resulting AnnData object as an .h5ad file.",
    )
    parser.add_argument(
        "--output_anndata",
        type=str,
        default="anndata",
        help="Output file name or path (used with --save).",
    )
    parser.add_argument(
        "--h5ad",
        type=str,
        default=None,
        help="File path for h5ad to load AnnData object.",
    )
    parser.add_argument(
        "--output_plots",
        type=str,
        default=None,
        help="Output directory for saving QC plots."

    )
    # add argument to print report 
    return parser.parse_args()


def main():
    args = arg_parser()
    path = args.dir_path
    action = args.action
    sep = args.sep
    verbose = args.verbose
    save = args.save
    output_anndata = args.output_anndata
    h5ad = args.h5ad
    output_plots = args.output_plots
    translate_sep = {"comma": ",", "tab": "\t"}
    if sep not in translate_sep:
        raise ValueError(
            f"Provided separator{sep} is not supported. Use either comma or tab."
        )
    run_parser = scParser(path, translate_sep[sep], verbose, save, output_anndata)
    parser_workflow = [run_parser.path_check, run_parser.sort_files,
                       run_parser.sort_content,run_parser.open_content]
    if action in ["parse","full"]:
        for step in parser_workflow:
            try:
                step()
            except Exception as e:
                raise Exception(f"Something went wrong!::{e}")
        if save:
            try:
                run_parser.jar_anndata()
            except:
                raise Exception("Something went wrong!")
        adata = run_parser.out_anndata() 
    if action in ["lint","full"]:
        if verbose:
            logger = Logger(verbose=verbose)
        if h5ad:
            try:
                adata = sc.read_h5ad(h5ad)
            except Exception as e:
                logger.log(f"Failed to load AnnData: {e}", severity="ERROR", source="main")
                return
        # run sclinter
        # Run exploratory analysis and linting
        basic_exploration(adata, output_dir=output_plots)
        issues = run_linter(adata, logger)
        print_report(issues, logger)

if __name__ == "__main__":
    main()
