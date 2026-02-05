import pandas as pd
from pathlib import Path

INPUT_DIR = Path("input_csv")
OUTPUT_DIR = Path("output_csv")

TARGET_COLS = [
    "firstName",
    "lastName",
    "phone",
    "state",
    "email",
    "companyName",
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files_missing_any = 0
total_rows = 0
rows_missing_any = 0
missing_per_col = pd.Series(0, index=TARGET_COLS)

for csv_file in INPUT_DIR.glob("*.csv"):
    print(f"Processing: {csv_file.name}")

    df = pd.read_csv(csv_file)

    # Ensure all target columns exist
    missing_cols = set(TARGET_COLS) - set(df.columns)
    if missing_cols:
        files_missing_any += 1
        for c in missing_cols:
            df[c] = ""

    # Keep and order columns
    df = df[TARGET_COLS]

    # Count missing values (NaN OR empty string)
    total_rows += len(df)

    missing = df.isna() | (df == "")
    rows_missing_any += missing.any(axis=1).sum()
    missing_per_col += missing.sum()

    # Remove duplicates by phone
    df = df.drop_duplicates(subset="phone")

    # Write output
    out_path = OUTPUT_DIR / f"{csv_file.stem}_ORGANIZED.csv"
    df.to_csv(out_path, index=False)

print("\n✅ All files processed.")
print(f"📊 Files missing ≥1 target column: {files_missing_any}")

print("\n📊 Data quality summary")
print(f"Total rows processed: {total_rows}")
print(f"Rows missing ≥1 target field: {rows_missing_any}")

print("\nMissing values per column:")
print(missing_per_col)
