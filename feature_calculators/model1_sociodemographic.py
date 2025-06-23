import pickle
import numpy as np
import pandas as pd
from feature_calculators.core import calculate_model_features

def calculate_features(patient_id, submission_id):
    # Step 1: Run core logic to get raw features
    raw_features = calculate_model_features(
        patient_id=patient_id,
        submission_id=submission_id,
        model_name='MRMR_COX_Sociodemographics',
        template_path='model_files/feature_templates/model1_sociodemographic_features.xlsx'
    )

    # Step 2: Convert to DataFrame
    df = pd.DataFrame([raw_features])
    # Fix misnamed features
    if 'Age.at.recruitment' in df.columns:
        df.rename(columns={'Age.at.recruitment': 'clinicalrisk_Age.at.recruitment'}, inplace=True)


    # Step 3: Load imputer and align input
    with open('model_files/imputers/model1_sociodemographics_rf (1).pkl', 'rb') as f:
        imputer = pickle.load(f)

    expected_features = imputer.feature_names_in_
    df = df.reindex(columns=expected_features, fill_value=0)
    
    # Step 4: Apply imputer
    df_imputed = pd.DataFrame(imputer.transform(df), columns=expected_features)
    

    # Step 5: Load and apply scaler (if applicable)
    try:
        with open('model_files/scalers/sociodemogrphic_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        if hasattr(scaler, 'feature_names_in_'):
            df_imputed = df_imputed.reindex(columns=scaler.feature_names_in_, fill_value=0)

        df_scaled = pd.DataFrame(scaler.transform(df_imputed.values), columns=df_imputed.columns)
    except FileNotFoundError:
        df_scaled = df_imputed  # Use imputed if no scaler is defined

    # After imputation + optional scaling
    if 'Age.at.recruitment' in df_scaled.columns:
        df_scaled.rename(columns={'Age.at.recruitment': 'clinicalrisk_Age.at.recruitment'}, inplace=True)


    # Step 6: Save final input to file (optional)
    out_path = f"model_outputs/patient_{patient_id}_model1_input_scaled.csv"
    df_scaled.to_csv(out_path, index=False)

    return df_scaled

