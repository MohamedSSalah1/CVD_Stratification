import pandas as pd

# Load the vertical CSV (your current file)
vertical_df = pd.read_csv("model_files/sociodemographicsSample (1).csv", header=None)

# Convert to wide format: row = 1 patient, columns = features
wide_df = vertical_df.set_index(0).T

# Fill with dummy values for testing if needed
for col in wide_df.columns:
    wide_df[col] = 0

# Save the clean version
wide_df.to_csv("model_files/correct_sociodemographics_sample.csv", index=False)
print("✅ Saved correct_sociodemographics_sample.csv with shape", wide_df.shape)

