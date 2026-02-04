import pandas as pd

# Target columns in desired order
TARGET_COLS = ["first_name", "last_name", "email", "company_name", "phone", "state"]
RENAME_MAP = {"first_name": "firstName", "last_name": "lastName", "company_name": "companyName"}

df = pd.read_csv("Indoor Sports Complexs_ Sports Complexs - NY.csv")

# Keep only target columns that exist; create missing ones as empty
for col in TARGET_COLS:
    if col not in df.columns:
        df[col] = ""

df = df[TARGET_COLS]

# rename columns to fit the Atlas contact template
df.rename(columns=RENAME_MAP, inplace=True)

# remove duplicates based on 'phone' column
df = df.drop_duplicates(subset=['phone'], keep='first')
df.to_csv("output.csv", index=False)