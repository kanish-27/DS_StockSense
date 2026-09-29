"""Data preparation pipeline — owned by Student 1 (Data Analyst).

Responsibility:
    Load the raw hackathon data, inspect and clean it, integrate multiple
    sources if there are several, and write ONE cleaned master dataset to
    ``data/processed/`` that Students 2 and 3 build on.

Status:
    Placeholder only. Implementation depends on confirming the actual dataset
    schema (files, columns, types, granularity) and the team's agreed output
    format. Record agreed names in ``src/common/config.py``.
"""

from src.common import config


def load_raw_data():
    """Load the raw data files from ``config.RAW_DATA_DIR``.

    TODO(Student 1): implement once the raw files are available and inspected.
    """
    raise NotImplementedError("Raw data loading not implemented yet.")


def clean_data(raw_data):
    """Handle missing values, duplicates, types, and invalid records.

    TODO(Student 1): document every cleaning decision (what, why, rows affected).
    """
    raise NotImplementedError("Data cleaning not implemented yet.")


def build_master_dataset(cleaned_data):
    """Integrate cleaned sources into the agreed master dataset.

    TODO(Student 1): agree the output columns/granularity with Students 2 and 3.
    """
    raise NotImplementedError("Master dataset integration not implemented yet.")


def main():
    """Run the full preparation pipeline end-to-end.

    TODO(Student 1): wire load -> clean -> integrate -> save to
    ``config.PROCESSED_DATA_DIR``.
    """
    print(f"Raw data dir:       {config.RAW_DATA_DIR}")
    print(f"Processed data dir: {config.PROCESSED_DATA_DIR}")
    print("TODO: data preparation pipeline not implemented yet.")


if __name__ == "__main__":
    main()
