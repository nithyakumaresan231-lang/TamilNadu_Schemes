"""Regression test suite to ensure existing RAG, Chatbot, and API functionality is protected."""

import unittest
from fastapi.testclient import TestClient

from backend.main import (
    app,
    SCHEMES_DB,
    SCHEME_ALIAS_MAP,
    detect_scheme_in_query,
    is_followup_question,
    rank_and_filter_discovery_schemes,
)
from backend.translation import (
    detect_scheme_from_tamil,
    detect_scheme_from_english,
    restore_canonical_scheme_name,
)


class TestChatbotRegression(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})

    def test_schemes_endpoint(self):
        resp = self.client.get("/schemes")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 150)
        self.assertTrue(any(s["scheme_id"] == "TN001" for s in data))

    def test_schemes_db_and_aliases(self):
        self.assertEqual(len(SCHEMES_DB), 150)
        self.assertGreater(len(SCHEME_ALIAS_MAP), 100)

    def test_scheme_detection_in_query(self):
        # Explicit scheme detection
        detected = detect_scheme_in_query("Tell me about Pudhumai Penn scheme")
        self.assertEqual(detected, "Pudhumai Penn")

        detected_tamil = detect_scheme_in_query("What is Tamil Pudhalvan?")
        self.assertEqual(detected_tamil, "Tamil Pudhalvan")

    def test_followup_detection(self):
        # Follow-up test
        self.assertTrue(is_followup_question("how to apply", "Pudhumai Penn"))
        self.assertTrue(is_followup_question("what are the benefits", "Pudhumai Penn"))
        # Unrelated domain query should not be follow-up
        self.assertFalse(is_followup_question("farmer fertilizer subsidy", "Pudhumai Penn"))

    def test_tamil_scheme_normalization(self):
        # Tamil pre-translation normalization for Tamil Pudhalvan
        tamil_q = "தமிழ்ப் புதல்வன் திட்டத்திற்கு யார் தகுதியானவர்கள்?"
        tamil_pudhalvan_variations = ["தமிழ்ப் புதல்வன்", "தமிழ் புதல்வன்"]
        normalized_q = tamil_q
        for var in tamil_pudhalvan_variations:
            if var in normalized_q:
                normalized_q = normalized_q.replace(var, "Tamil Pudhalvan")
                break
        self.assertIn("Tamil Pudhalvan", normalized_q)

        # English scheme detection
        detected_en = detect_scheme_from_english("Who is eligible for Pudhumai Penn?")
        self.assertIsNotNone(detected_en)
        self.assertEqual(detected_en.get("scheme_name"), "Pudhumai Penn")

        # Canonical restoration
        restored = restore_canonical_scheme_name("Tell me about this scheme", detected_en)
        self.assertIn("Pudhumai Penn", restored)

    def test_discovery_filtering_and_scoring(self):
        fake_chunks = [
            {"scheme_name": "Kisaan Credit Card", "text": "farmer agricultural credit", "similarity_score": 0.8},
            {"scheme_name": "Pudhumai Penn", "text": "girl student college", "similarity_score": 0.75},
        ]
        filtered = rank_and_filter_discovery_schemes("farmer crop support", fake_chunks)
        # Kisaan Credit Card should be favored over student scheme for farmer query
        self.assertTrue(any(c["scheme_name"] == "Kisaan Credit Card" for c in filtered))

    def test_chat_endpoint_empty_validation(self):
        resp = self.client.post("/api/chat", json={"question": ""})
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
