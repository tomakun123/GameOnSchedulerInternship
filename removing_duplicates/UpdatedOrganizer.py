import pandas as pd
from pathlib import Path

INPUT_DIR = Path("input_csv")
OUTPUT_DIR = Path("output_csv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COLS = ["firstName", "lastName", "phoneNumber", "state", "email", "companyName"]

RENAME_MAP = {
    "first_name": "firstName",
    "last_name": "lastName",
    "company_name": "companyName",
}

def is_blank(s: pd.Series) -> pd.Series:
    s = s.astype(str)
    return s.isna() | s.str.strip().eq("") | s.str.strip().str.lower().eq("nan")

files_processed = 0

rows_before = 0
rows_after = 0

blank_before = pd.Series(0, index=TARGET_COLS)
blank_after = pd.Series(0, index=TARGET_COLS)

for csv_file in INPUT_DIR.glob("*.csv"):
    files_processed += 1
    print(f"Processing: {csv_file.name}")

    df = pd.read_csv(csv_file, dtype=str).rename(columns=RENAME_MAP)

    # Ensure target columns exist
    for col in TARGET_COLS:
        if col not in df.columns:
            df[col] = ""

    df = df[TARGET_COLS]
    
    # Replace blank/empty values with "N/A"
    for col in TARGET_COLS:
        df.loc[is_blank(df[col]), col] = "N/A"
        
    # append '1' to phone numbers that don't start with '1' and aren't "N/A"
    pn = df["phoneNumber"].astype(str).str.strip()
    mask = pn.ne("N/A") & ~pn.str.startswith("1")
    df.loc[mask, "phoneNumber"] = "1" + pn[mask]

    # ---------- BEFORE DEDUPE COUNTS ----------
    rows_before += len(df)
    blank_before += (df.apply(is_blank)).sum()

    # Normalize phone for dedupe key
    df["_phone_key"] = (
        df["phoneNumber"]
        .astype(str)
        .str.replace(r"\s+", "", regex=True)
        .str.strip()
    )

    # Score rows by how much info they have (exclude phone)
    info_cols = [c for c in TARGET_COLS if c != "phone"]
    df["_info_score"] = (~df[info_cols].apply(is_blank)).sum(axis=1)

    # Deduplicate: keep row with highest info score per phone
    df = (
        df.sort_values(by=["_phone_key", "_info_score"], ascending=[True, False])
          .drop_duplicates(subset="_phone_key", keep="first")
          .drop(columns=["_phone_key", "_info_score"])
    )

    # ---------- AFTER DEDUPE COUNTS ----------
    rows_after += len(df)
    blank_after += (df.apply(is_blank)).sum()

    out_path = OUTPUT_DIR / f"{csv_file.stem}_ORGANIZED.csv"
    df.to_csv(out_path, index=False)

# ---------------- SUMMARY ----------------
print("\n✅ Done.")
print(f"Files processed: {files_processed}")

print("\n📊 Row counts")
print(f"Rows BEFORE dedupe: {rows_before}")
print(f"Rows AFTER dedupe:  {rows_after}")
print(f"Rows removed:       {rows_before - rows_after}")

print("\n📊 Blank counts BEFORE dedupe")
print(blank_before)

print("\n📊 Blank counts AFTER dedupe")
print(blank_after)

print("\n📊 Improvement (blanks removed)")
print(blank_before - blank_after)
