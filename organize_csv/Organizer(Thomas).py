import pandas as pd
from pathlib import Path

INPUT_DIR = Path("input_csv")
OUTPUT_DIR = Path("output_csv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_COLS = ["firstName", "lastName", "phone", "state", "email", "companyName"]

# Column positions (0-indexed) from your CSV header order:
# query(0), name(1), name_for_emails(2), subtype(3), category(4), type(5),
# phone(6), website(7), address(8), street(9), city(10), county(11),
# state(12), state_code(13), postal_code(14), country(15), country_code(16),
# domain(17), company_name(18), company_phone(19), company_phones(20),
# company_linkedin(21), company_facebook(22), company_instagram(23),
# company_x(24), company_youtube(25), full_name(26), first_name(27),
# last_name(28), title(29), email(30), ...
COL_POSITIONS = {
    27: "firstName",
    28: "lastName",
    19: "phone",
    13: "state",
    30: "email",
    18: "companyName",
}

def is_blank(s: pd.Series) -> pd.Series:
    s = s.astype("string")
    return s.isna() | s.str.strip().eq("")

files_processed = 0
rows_before = 0
rows_after = 0

blank_before = pd.Series(0, index=TARGET_COLS, dtype="int64")
blank_after  = pd.Series(0, index=TARGET_COLS, dtype="int64")

for csv_file in INPUT_DIR.glob("*.csv"):
    files_processed += 1
    print(f"Processing: {csv_file.name}")

    # Read without headers, select only the columns we need by position
    raw = pd.read_csv(csv_file, dtype=str, header=None, skiprows=0)

    # Build df with only our target columns, named correctly
    df = pd.DataFrame()
    for pos, col_name in COL_POSITIONS.items():
        if pos < len(raw.columns):
            df[col_name] = raw.iloc[:, pos]
        else:
            df[col_name] = ""

    # Reorder to match TARGET_COLS
    df = df[TARGET_COLS]

    # ----- BEFORE COUNTS -----
    rows_before += len(df)
    missing_before_df = df.apply(is_blank)
    blank_before += missing_before_df.sum()

    # ----- DEDUPE (keep row with most non-blank fields, per phone) -----
    # normalize phone key (digits only)
    phone_key = (
        df["phone"]
        .astype("string")
        .fillna("")
        .str.replace(r"\D+", "", regex=True)   # keep digits only
        .str.strip()
    )

    # score by non-blank fields (excluding phone itself)
    info_cols = [c for c in TARGET_COLS if c != "phone"]
    info_score = (~df[info_cols].apply(is_blank)).sum(axis=1)

    df2 = df.copy()
    df2["_phone_key"] = phone_key
    df2["_info_score"] = info_score

    # split: rows with a phone key vs without
    has_phone = df2["_phone_key"].ne("")
    with_phone = df2[has_phone]
    no_phone = df2[~has_phone].drop(columns=["_phone_key", "_info_score"])

    # dedupe only rows that actually have a phone
    with_phone = (
        with_phone.sort_values(by=["_phone_key", "_info_score"], ascending=[True, False])
                  .drop_duplicates(subset="_phone_key", keep="first")
                  .drop(columns=["_phone_key", "_info_score"])
    )

    df_final = pd.concat([with_phone, no_phone], ignore_index=True)

    # ----- AFTER COUNTS -----
    rows_after += len(df_final)
    missing_after_df = df_final.apply(is_blank)
    blank_after += missing_after_df.sum()

    out_path = OUTPUT_DIR / f"{csv_file.stem}_ORGANIZED.csv"
    df_final.to_csv(out_path, index=False)

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
