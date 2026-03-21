import pandas as pd

df = pd.read_csv("data/cardio_train.csv", sep=";")
print(f"Original rows: {len(df)}")

# Remove invalid blood pressure values
df = df[df["ap_hi"] > 0]
df = df[df["ap_lo"] > 0]
df = df[df["ap_hi"] > df["ap_lo"]]

print(f"Cleaned rows: {len(df)}")
print(f"Rows removed: {70000 - len(df)}")

df.to_csv("data/cardio_clean.csv", index=False)
print("Saved to data/cardio_clean.csv")
