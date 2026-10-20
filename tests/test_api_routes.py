"""Tests for the recommendation API routes."""

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.recommendation_routes import router


class TestRecommendationRoutes(unittest.TestCase):

    def setUp(self):
        # Create an isolated test FastAPI app mounting only the recommendations router
        self.test_app = FastAPI()
        self.test_app.include_router(router)
        self.client = TestClient(self.test_app)

    def test_post_recommendations_success(self):
        payload = {
            "age": 22,
            "gender": "female",
            "category": "SC",
            "annual_income": 200000.0,
            "education_level": "undergraduate",
            "government_school": "yes",
            "current_student_status": "yes",
        }
        response = self.client.post("/api/recommendations", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_schemes_evaluated", data)
        self.assertIn("recommendations", data)
        self.assertGreater(data["total_schemes_evaluated"], 0)
        self.assertGreaterEqual(data["likely_matches_count"] + data["needs_verification_count"], 1)

    def test_post_recommendations_empty_profile(self):
        # All fields optional
        response = self.client.post("/api/recommendations", json={})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_schemes_evaluated"], 150)
        self.assertGreater(data["needs_verification_count"], 0)

    def test_post_recommendations_invalid_age(self):
        response = self.client.post("/api/recommendations", json={"age": -10})
        self.assertEqual(response.status_code, 422)  # Pydantic validation error

    def test_post_recommendations_invalid_income(self):
        response = self.client.post("/api/recommendations", json={"annual_income": -500})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
