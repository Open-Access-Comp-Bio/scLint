import argparse
from scLint.sc_parser import scParser


def arg_parser():
    """
    Custom argument parser using argparse
    Input:
        The only required input is dir_path
    Output
        Outputs the parser object
    """
    parser = argparse.ArgumentParser(
        description="scParser, a tool for sorting scRNA files into an AnnData Object."
    )
    parser.add_argument(
        "dir_path",
        help="Required. Pathway to directory with scRNA count files, metadata, etc.",
    )
    parser.add_argument(
        "--sep",
        default="tab",
        help="Deliminator/separatorused throughout the files within dir_path. Default is tab.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print progress messages."
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the resulting AnnData object as an .h5ad file.",
    )
    parser.add_argument(
        "--output",
        default="anndata",
        help="Output file name or path (used with --save).",
    )
    return parser.parse_args()


def main():
    args = arg_parser()
    path = args.dir_path
    sep = args.sep
    verbose = args.verbose
    save = args.save
    output = args.output
    translate_sep = {"comma": ",", "tab": "\t"}
    if sep not in translate_sep:
        raise ValueError(
            f"Provided separator{sep} is not supported. Use either comma or tab."
        )
    run_parser = scParser(path, translate_sep[sep], verbose, save, output)
    run_parser.path_check()
    run_parser.sort_files()
    run_parser.sort_content()
    run_parser.open_content()
    run_parser.gen_anndata()
    if save:
        run_parser.jar_anndata()


if __name__ == "__main__":
    main()
