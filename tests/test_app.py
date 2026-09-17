"""Backend API tests for the extracurricular activities application."""

import copy
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

import app as application  # noqa: E402


class ActivitiesApiTests(unittest.TestCase):
    """Exercise the public FastAPI endpoints using Arrange-Act-Assert tests."""

    def setUp(self):
        self.client = TestClient(application.app)
        self.original_activities = copy.deepcopy(application.activities)

    def tearDown(self):
        application.activities.clear()
        application.activities.update(self.original_activities)

    def test_lists_available_activities(self):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = self.client.get("/activities")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(expected_activity, response.json())

    def test_signup_rejects_duplicate_participant(self):
        # Arrange
        activity = "Basketball Team"
        email = "student@mergington.edu"

        # Act
        first_response = self.client.post(
            f"/activities/{activity}/signup", params={"email": email}
        )
        duplicate_response = self.client.post(
            f"/activities/{activity}/signup", params={"email": email}
        )

        # Assert
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(
            duplicate_response.json()["detail"], "Student is already signed up"
        )

    def test_unregister_removes_participant(self):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = self.client.delete(
            f"/activities/{activity}/unregister", params={"email": email}
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(email, application.activities[activity]["participants"])

    def test_unknown_activity_returns_not_found(self):
        # Arrange
        activity = "Missing Club"

        # Act
        response = self.client.post(
            f"/activities/{activity}/signup",
            params={"email": "student@mergington.edu"},
        )

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Activity not found")


if __name__ == "__main__":
    unittest.main()
