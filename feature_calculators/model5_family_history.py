import pickle
import numpy as np
import pandas as pd
from feature_calculators.core import calculate_model_features

def calculate_features(patient_id, submission_id):
    # Step 1: Run core logic to get raw features
    raw_features = calculate_model_features(
        patient_id=patient_id,
        submission_id=submission_id,
        model_name='MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history',
        template_path='model_files/feature_templates/model5_Familyhistory_features.xlsx'
    )

    # Step 2: Convert to DataFrame
    df = pd.DataFrame([raw_features])

    # Step 3: Load imputer and align input
    with open('model_files/imputers/familyHistorynoDrop_rf.pkl', 'rb') as f:
        imputer = pickle.load(f)

    expected_imputer_features = imputer.feature_names_in_
    df = df.reindex(columns=expected_imputer_features, fill_value=0)

    # Step 4: Apply imputer
    df_imputed = pd.DataFrame(imputer.transform(df), columns=expected_imputer_features)

    # Step 5: Load scaler and align input (if applicable)
    try:
        with open('model_files/scalers/familyHistorynoDropscaler.pkl', 'rb') as f:
            scaler = pickle.load(f)

        if hasattr(scaler, 'feature_names_in_'):
            df_imputed = df_imputed.reindex(columns=scaler.feature_names_in_, fill_value=0)

        df_scaled = pd.DataFrame(scaler.transform(df_imputed), columns=df_imputed.columns)
    except FileNotFoundError:
        df_scaled = df_imputed

    # Step 6: Save final input to file (optional)
    out_path = f"model_outputs/patient_{patient_id}_model5_input_scaled.csv"
    df_scaled.to_csv(out_path, index=False)

    return df_scaled
