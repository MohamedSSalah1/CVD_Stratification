from django.core.management.base import BaseCommand
from accounts.models import CVD_Risk_Model_InputFeatures, CVD_Risk_FeatureThresholds
import pandas as pd
import os
import re

class Command(BaseCommand):
    help = 'Load thresholds for tertile features into CVD_Risk_FeatureThresholds table'

    def handle(self, *args, **options):
        threshold_path = os.path.join('Questionnaire_data', 'Thirds_threshold_values.xlsx')

        try:
            df = pd.read_excel(threshold_path).dropna(subset=["columnName", "threshold"])
            df["columnName"] = df["columnName"].astype(str).str.strip()
        except Exception as e:
            self.stderr.write(f"❌ Failed to read threshold Excel: {e}")
            return

        # 🔁 Step 1: Group thresholds by base
        base_dict = {}
        for _, row in df.iterrows():
            name = row["columnName"]
            threshold = row["threshold"]
            match = re.match(r"(.+?)_(Lower|Middle|Upper)\.third", name)
            if match:
                base, tertile = match.groups()
                base_dict.setdefault(base, {})[f"{tertile} third"] = threshold

        created = 0
        for base, thresholds in base_dict.items():
            for tertile, value in thresholds.items():
                full_feature_name = f"{base}_{tertile.replace(' ', '.')}"
                try:
                    feature = CVD_Risk_Model_InputFeatures.objects.get(feature_name__icontains=full_feature_name)
                except CVD_Risk_Model_InputFeatures.DoesNotExist:
                    self.stderr.write(f"⚠️ No matching feature in DB: {full_feature_name}")
                    continue

                _, is_created = CVD_Risk_FeatureThresholds.objects.get_or_create(
                    feature=feature,
                    threshold_type=tertile,
                    defaults={"threshold_value": value}
                )
                if is_created:
                    self.stdout.write(f"✅ Added threshold: {full_feature_name} → {tertile} = {value}")
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"\n📊 Done: {created} thresholds added."))

