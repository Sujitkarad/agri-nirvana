import unittest

from backend.ml.inference.dynamic_advisor import generate_dynamic_advisory


class TestAdvisorySafety(unittest.TestCase):
    def test_advisor_never_generates_a_dose(self):
        result = generate_dynamic_advisory(
            crop="Tomato",
            disease="Tomato Early Blight",
            pathogen="Alternaria solani",
            severity_tier="Moderate",
            necrotic_area_pct=24.0,
            confidence_pct=88,
            differential_diagnoses=[],
            base_info={
                "symptoms_observed": ["Target-like lesions"],
                "likely_cause": "Warm, wet conditions",
                "immediate_precautions": ["Scout the crop"],
                "treatment_organic": ["Use a registered biological product according to its label"],
                "treatment_chemical": ["Use a registered fungicide according to its label"],
                "prevention_tips": ["Avoid prolonged leaf wetness"],
            },
        )
        self.assertFalse(result["treatment_allowed"])
        self.assertTrue(result["reference_only"])
        self.assertTrue(result["ipm"]["tier_2_chemical"][0]["verification_required"])
        self.assertIsNone(result["ipm"]["tier_2_chemical"][0]["dosage"])
        self.assertIsNone(result["ipm"]["tier_2_chemical"][0]["dose_ml_per_15L"])

    def test_advisor_does_not_fabricate_missing_evidence(self):
        result = generate_dynamic_advisory(
            crop="Tomato",
            disease="Unknown Disease",
            pathogen="",
            severity_tier="Unknown",
            necrotic_area_pct=0,
            confidence_pct=0,
            differential_diagnoses=[],
            base_info={},
        )
        self.assertFalse(result["treatment_allowed"])
        self.assertIn("not established", result["likely_cause"])
        self.assertEqual(result["ipm"]["tier_2_chemical"], [])


if __name__ == "__main__":
    unittest.main()
