import pandas as pd
from pathlib import Path

# -------- CONFIG --------
INPUT_DIR = Path("input_csv")      # folder with raw CSVs
OUTPUT_DIR = Path("output_csv") # folder for cleaned CSVs

TARGET_COLS = ["first_name", "last_name", "phone", "state", "email", "company_name"]
RENAME_MAP = {
    "first_name": "firstName",
    "last_name": "lastName",
    "company_name": "companyName"
}
# ------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for csv_file in INPUT_DIR.glob("*.csv"):
    print(f"Processing: {csv_file.name}")

    df = pd.read_csv(csv_file)

    # Ensure all target columns exist
    for col in TARGET_COLS:
        if col not in df.columns:
            df[col] = ""

    # Keep and order columns
    df = df[TARGET_COLS]

    # Rename for Atlas template
    df.rename(columns=RENAME_MAP, inplace=True)

    # Remove duplicates by phone
    df = df.drop_duplicates(subset=["phone"], keep="first")

    # Build output filename
    output_name = f"{csv_file.stem}_ORGANIZED.csv"
    output_path = OUTPUT_DIR / output_name

    df.to_csv(output_path, index=False)

print("✅ All files processed.")
