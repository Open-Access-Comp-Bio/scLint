from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve() / "collateral" / "scdata"
pool_files_ans = {
    "dir": Path(ROOT_DIR),
    "files": [
        Path(ROOT_DIR / "GSE162170_rna_cell_names.txt"),
        Path(ROOT_DIR / "GSE162170_rna_cell_metadata.txt"),
        Path(ROOT_DIR / "subset_GSE162170_raw_rna_counts.tsv"),
        Path(ROOT_DIR / "subset_GSE162170_rna_unspliced_counts.tsv"),
        Path(ROOT_DIR / "GSE162170_rna_sample_qc.tsv.gz"),
        Path(ROOT_DIR / "subset_GSE162170_rna_spliced_counts.tsv"),
    ],
}
id_files_ans = {
    "uns": [
        Path(ROOT_DIR / "GSE162170_rna_cell_names.txt"),
        Path(ROOT_DIR / "GSE162170_rna_sample_qc.tsv.gz"),
    ],
    "obs": Path(ROOT_DIR / "GSE162170_rna_cell_metadata.txt"),
    "X": Path(ROOT_DIR / "subset_GSE162170_raw_rna_counts.tsv"),
    "unspliced": Path(ROOT_DIR / "subset_GSE162170_rna_unspliced_counts.tsv"),
    "spliced": Path(ROOT_DIR / "subset_GSE162170_rna_spliced_counts.tsv"),
}
