"""
Unit tests for FastAPI activities endpoints.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data is ready
        ACT: GET /activities
        ASSERT: Response contains all 9 activities with correct structure
        """
        # Act
        response = client_with_sample_data.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_returns_correct_structure(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data is ready
        ACT: GET /activities
        ASSERT: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client_with_sample_data.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_returns_correct_participant_data(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data is ready
        ACT: GET /activities
        ASSERT: Participant data is accurate for known activities
        """
        # Act
        response = client_with_sample_data.get("/activities")
        activities = response.json()

        # Assert
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_for_new_student(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, new student email ready
        ACT: POST /activities/Chess%20Club/signup?email=newstudent@mergington.edu
        ASSERT: Response indicates success and status 200
        """
        # Act
        response = client_with_sample_data.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, new student email ready
        ACT: POST /activities/Tennis%20Club/signup?email=newstudent@mergington.edu
        ASSERT: Participant is added to the activity's participants list
        """
        # Act
        client_with_sample_data.post(
            "/activities/Tennis Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        response = client_with_sample_data.get("/activities")
        activities = response.json()

        # Assert
        assert "newstudent@mergington.edu" in activities["Tennis Club"]["participants"]
        assert len(activities["Tennis Club"]["participants"]) == 3  # Originally 2

    def test_signup_fails_with_404_for_nonexistent_activity(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, nonexistent activity name ready
        ACT: POST /activities/Nonexistent%20Club/signup?email=student@mergington.edu
        ASSERT: Response status is 404 with "Activity not found" message
        """
        # Act
        response = client_with_sample_data.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_fails_with_400_if_student_already_signed_up(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, student already in Chess Club
        ACT: POST /activities/Chess%20Club/signup?email=michael@mergington.edu
        ASSERT: Response status is 400 with "already signed up" message
        """
        # Act
        response = client_with_sample_data.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_increments_participant_count(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, track initial count
        ACT: POST /activities/Programming%20Class/signup?email=newstudent@mergington.edu
        ASSERT: Participant count increases by 1
        """
        # Arrange
        initial_response = client_with_sample_data.get("/activities")
        initial_count = len(initial_response.json()["Programming Class"]["participants"])

        # Act
        client_with_sample_data.post(
            "/activities/Programming Class/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        updated_response = client_with_sample_data.get("/activities")
        updated_count = len(updated_response.json()["Programming Class"]["participants"])

        # Assert
        assert updated_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful_for_existing_participant(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, existing participant email ready
        ACT: DELETE /activities/Chess%20Club/unregister?email=michael@mergington.edu
        ASSERT: Response indicates success and status 200
        """
        # Act
        response = client_with_sample_data.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert "michael@mergington.edu" in response.json()["message"]

    def test_unregister_removes_participant_from_activity(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, participant in Tennis Club
        ACT: DELETE /activities/Tennis%20Club/unregister?email=lucas@mergington.edu
        ASSERT: Participant is removed from the activity's participants list
        """
        # Act
        client_with_sample_data.delete(
            "/activities/Tennis Club/unregister",
            params={"email": "lucas@mergington.edu"}
        )
        response = client_with_sample_data.get("/activities")
        activities = response.json()

        # Assert
        assert "lucas@mergington.edu" not in activities["Tennis Club"]["participants"]
        assert len(activities["Tennis Club"]["participants"]) == 1  # Originally 2

    def test_unregister_fails_with_404_for_nonexistent_activity(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, nonexistent activity name ready
        ACT: DELETE /activities/Fake%20Club/unregister?email=student@mergington.edu
        ASSERT: Response status is 404 with "Activity not found" message
        """
        # Act
        response = client_with_sample_data.delete(
            "/activities/Fake Club/unregister",
            params={"email": "student@mergington.edu"}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_fails_with_400_if_student_not_registered(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, student NOT in Basketball Team
        ACT: DELETE /activities/Basketball%20Team/unregister?email=student@mergington.edu
        ASSERT: Response status is 400 with "not registered" message
        """
        # Act
        response = client_with_sample_data.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "student@mergington.edu"}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_decrements_participant_count(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data, track initial count
        ACT: DELETE /activities/Art%20Studio/unregister?email=grace@mergington.edu
        ASSERT: Participant count decreases by 1
        """
        # Arrange
        initial_response = client_with_sample_data.get("/activities")
        initial_count = len(initial_response.json()["Art Studio"]["participants"])

        # Act
        client_with_sample_data.delete(
            "/activities/Art Studio/unregister",
            params={"email": "grace@mergington.edu"}
        )
        updated_response = client_with_sample_data.get("/activities")
        updated_count = len(updated_response.json()["Art Studio"]["participants"])

        # Assert
        assert updated_count == initial_count - 1


class TestIntegrationSignupAndUnregister:
    """Integration tests for signup followed by unregister."""

    def test_signup_then_unregister_returns_to_original_state(self, client_with_sample_data):
        """
        ARRANGE: TestClient with sample data
        ACT: POST signup, then DELETE unregister for same student
        ASSERT: Participant count returns to original value
        """
        # Arrange
        initial_response = client_with_sample_data.get("/activities")
        initial_count = len(initial_response.json()["Drama Club"]["participants"])

        # Act - Signup
        client_with_sample_data.post(
            "/activities/Drama Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )

        # Act - Unregister
        client_with_sample_data.delete(
            "/activities/Drama Club/unregister",
            params={"email": "newstudent@mergington.edu"}
        )

        # Assert
        final_response = client_with_sample_data.get("/activities")
        final_count = len(final_response.json()["Drama Club"]["participants"])
        assert final_count == initial_count
