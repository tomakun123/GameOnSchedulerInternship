import pandas as pd

df = pd.read_csv("Indoor Sports Complexs_ Sports Complexs - AZ.csv")
df = df.drop_duplicates(subset=['phone'])
df.to_csv("output.csv", index=False)