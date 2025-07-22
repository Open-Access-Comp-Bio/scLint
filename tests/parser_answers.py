import os
from pathlib import PosixPath
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve() / "collateral" / "scdata"
pool_files_ans = {
    "dir": PosixPath(ROOT_DIR),
    "files": [
        PosixPath(ROOT_DIR / "GSE162170_rna_cell_names.txt"),
        PosixPath(ROOT_DIR / "GSE162170_rna_cell_metadata.txt"),
        PosixPath(ROOT_DIR / "subset_GSE162170_raw_rna_counts.tsv"),
        PosixPath(ROOT_DIR / "subset_GSE162170_rna_unspliced_counts.tsv"),
        PosixPath(ROOT_DIR / "GSE162170_rna_sample_qc.tsv.gz"),
        PosixPath(ROOT_DIR / "subset_GSE162170_rna_spliced_counts.tsv"),
    ],
}
id_files_ans = {
    "uns": [
        PosixPath(ROOT_DIR / "GSE162170_rna_cell_names.txt"),
        PosixPath(ROOT_DIR / "GSE162170_rna_sample_qc.tsv.gz"),
    ],
    "obs": PosixPath(ROOT_DIR / "GSE162170_rna_cell_metadata.txt"),
    "X": PosixPath(ROOT_DIR / "subset_GSE162170_raw_rna_counts.tsv"),
    "unspliced": PosixPath(ROOT_DIR / "subset_GSE162170_rna_unspliced_counts.tsv"),
    "spliced": PosixPath(ROOT_DIR / "subset_GSE162170_rna_spliced_counts.tsv"),
}
