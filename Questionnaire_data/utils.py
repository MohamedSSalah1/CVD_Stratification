from accounts.models import CVD_risk_Questionnaire
import pandas as pd

# 👇 Extracts conditional question IDs that depend on sex from the Excel mapping file
def get_sex_based_dependencies():
    file_path = 'Questionnaire_data/TS_advanced_mapping_v2 (1).xlsx'
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()

    # Filter rows where Q31 ("sex") is used as a determining factor
    df = df[df['Determined.by'] == 31]

    dependencies = []
    for _, row in df.iterrows():
        try:
            qid = int(float(row['Field.ID']))
            sex_code = int(float(row['Answer']))  # 1 = Male, 0 = Female
            sex = 'Male' if sex_code == 1 else 'Female' if sex_code == 0 else None

            # Only add if question exists in the database and sex is valid
            if sex and CVD_risk_Questionnaire.objects.filter(question_id=qid).exists():
                dependencies.append((qid, sex))
        except Exception:
            continue  # Skip invalid rows silently

    return dependencies


# 👇 Filters out questions not relevant to the patient's biological sex
def get_visible_questions_for_patient_in_category(patient, category):
    patient_sex = patient.sex  # Updated field name

    # Get all questions in this category
    all_questions = CVD_risk_Questionnaire.objects.filter(category=category).order_by('question_order')

    # Get all sex-based question dependencies
    sex_deps = get_sex_based_dependencies()

    # Exclude questions that do not match patient's sex
    excluded_qids = [qid for qid, sex in sex_deps if sex != patient_sex]

    return all_questions.exclude(question_id__in=excluded_qids)
