import pandas as pd
import os
import re
from django.db import connections
from django.utils import timezone
from accounts.models import (
    CVD_risk_Responses,
    CVD_ModelFeatureMappings,
    CVD_Risk_FeatureThresholds,
    CVD_Risk_CalculatedFeatures,
    FeatureOptionMapping,
    ML_Models,
)

def calculate_model_features(patient_id, submission_id, model_name, template_path):
    """
    Reusable feature calculation logic for any model.
    Ensures conditional/unanswered features (e.g. sex-specific) are defaulted to 0.
    """

    connections.close_all()  # Ensure no leftover transactions
    
    # 1. Load expected features from Excel
    try:
        feature_order = pd.read_excel(template_path, header=None)[0].tolist()
    except Exception as e:
        print(f"❌ Error loading feature template: {e}")
        return

    # 2. Load model from DB
    try:
        model = ML_Models.objects.get(model_name=model_name)
    except ML_Models.DoesNotExist:
        print(f"❌ Model not found in DB: {model_name}")
        return

    # 3. Load feature mappings
    mappings = CVD_ModelFeatureMappings.objects.filter(model=model).select_related('input_feature')
    model_features = {m.input_feature.feature_name: m.input_feature for m in mappings}

    # 4. Initialize feature values to 0
    feature_values = {fname: 0 for fname in feature_order}

    # 5. Tertile grouping
    tertile_groups = {}
    for fname in feature_order:
        clean_name = re.sub(r'^category_.*?_ts_', '', fname).strip()
        if any(suffix in clean_name for suffix in ['_Lower.third', '_Middle.third', '_Upper.third']):
            base = clean_name.rsplit('_', 1)[0]
            tertile_groups.setdefault(base, []).append((fname, clean_name))

    # 6. Calculate feature values from responses
    for fname in feature_order:
        full_feature_name = re.sub(r'^category_.*?_ts_', '', fname).strip()

        if full_feature_name not in model_features:
            print(f"⚠️ Input feature not in DB: {full_feature_name}")
            continue

        feature_obj = model_features[full_feature_name]
        question = feature_obj.question

        try:
            response = CVD_risk_Responses.objects.filter(
                patient_id=patient_id,
                question=question
            ).order_by('-last_updated').first()

            # If no response exists, default 0 already set — skip
            if not response:
                continue

            # === A. Numeric (Tertile) ===
            if response.response_type == 'Enter integer answer' and response.numeric_response is not None:
                val = response.numeric_response
                base_name = full_feature_name.rsplit('_', 1)[0]

                if base_name in tertile_groups:
                    triplet = tertile_groups[base_name]
                    thresholds_by_suffix = {}

                    for col_name, clean_name in triplet:
                        feat_obj = model_features.get(clean_name)
                        if not feat_obj:
                            continue
                        suffix = clean_name.rsplit('_', 1)[-1]
                        threshold = CVD_Risk_FeatureThresholds.objects.filter(
                            feature=feat_obj
                        ).values_list('threshold_value', flat=True).first()
                        if threshold is not None:
                            thresholds_by_suffix[suffix] = (col_name, threshold)

                    # Infer missing thresholds if needed
                    try:
                        suffixes = thresholds_by_suffix.keys()
                        if 'Lower.third' in suffixes and 'Upper.third' in suffixes and 'Middle.third' not in suffixes:
                            lower_val = thresholds_by_suffix['Lower.third'][1]
                            upper_val = thresholds_by_suffix['Upper.third'][1]
                            middle_val = (lower_val + upper_val) / 2
                            middle_col = next((f for f in feature_order if f.endswith('_Middle.third') and base_name in f), None)
                            if middle_col:
                                thresholds_by_suffix['Middle.third'] = (middle_col, middle_val)
                        elif 'Lower.third' in suffixes and 'Middle.third' in suffixes and 'Upper.third' not in suffixes:
                            lower_val = thresholds_by_suffix['Lower.third'][1]
                            middle_val = thresholds_by_suffix['Middle.third'][1]
                            upper_val = 2 * middle_val - lower_val
                            upper_col = next((f for f in feature_order if f.endswith('_Upper.third') and base_name in f), None)
                            if upper_col:
                                thresholds_by_suffix['Upper.third'] = (upper_col, upper_val)
                        elif 'Middle.third' in suffixes and 'Upper.third' in suffixes and 'Lower.third' not in suffixes:
                            middle_val = thresholds_by_suffix['Middle.third'][1]
                            upper_val = thresholds_by_suffix['Upper.third'][1]
                            lower_val = 2 * middle_val - upper_val
                            lower_col = next((f for f in feature_order if f.endswith('_Lower.third') and base_name in f), None)
                            if lower_col:
                                thresholds_by_suffix['Lower.third'] = (lower_col, lower_val)
                    except Exception as e:
                        print(f"❌ Error inferring thresholds for {base_name}: {e}")

                    # Apply encoding
                    if 'Lower.third' in thresholds_by_suffix and val <= thresholds_by_suffix['Lower.third'][1]:
                        feature_values[thresholds_by_suffix['Lower.third'][0]] = 1
                    elif 'Middle.third' in thresholds_by_suffix and val <= thresholds_by_suffix['Middle.third'][1]:
                        feature_values[thresholds_by_suffix['Middle.third'][0]] = 1
                    elif 'Upper.third' in thresholds_by_suffix:
                        feature_values[thresholds_by_suffix['Upper.third'][0]] = 1
                else:
                    feature_values[fname] = float(val)

            # === B. Single-Select ===
            elif response.response_type == 'Select one answer':
                try:
                    mapping = FeatureOptionMapping.objects.get(feature_name=full_feature_name)
                    if response.option_selected and response.option_selected.id == mapping.option.id:
                        feature_values[fname] = 1
                except Exception:
                    pass

            # === C. Multi-Select ===
            elif response.response_type == 'Toggle multiple answer':
                try:
                    mapping = FeatureOptionMapping.objects.get(feature_name=full_feature_name)
                    selected_ids = [opt.id for opt in response.multi_selected_options.all()]
                    if mapping.option.id in selected_ids:
                        feature_values[fname] = 1
                except Exception:
                    pass

        except Exception as e:
            print(f"❌ Error processing feature {full_feature_name}: {e}")
            continue

    # 7. Save to DB — no transactions to avoid savepoint issues
    connections.close_all()
    saved_count = 0
    skipped_unmapped = 0
    timestamp = timezone.now()

    for fname, value in feature_values.items():
        full_feature_name = re.sub(r'^category_.*?_ts_', '', fname).strip()

        if full_feature_name not in model_features:
            skipped_unmapped += 1
            continue

        feature_obj = model_features[full_feature_name]

        try:
            #connections.close_all()
            CVD_Risk_CalculatedFeatures.objects.update_or_create(
                patient_id=patient_id,
                model=model,
                feature=feature_obj,
                defaults={'value': value, 'created_at': timestamp}
            )
            saved_count += 1
        except Exception as e:
            print(f"❌ Error saving feature {full_feature_name} with value {value}: {e}")
            connections.close_all()
            continue

    print(f"⚠️ Skipped {skipped_unmapped} unmapped features (not present in model DB mappings)")
    print(f"✅ Saved or updated {saved_count} features for patient {patient_id}")

    # 8. Export for debugging
    try:
        df_out = pd.DataFrame([feature_values])
        os.makedirs("model_outputs", exist_ok=True)
        out_path = f"model_outputs/patient_{patient_id}_{model_name}_input.csv"
        df_out.to_csv(out_path, index=False)
        print(f"📁 CSV saved to: {out_path}")
    except Exception as e:
        print(f"❌ Failed to save CSV: {e}")

    return feature_values
