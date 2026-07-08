from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_status_code = 200

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == expected_status_code
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_and_prevents_duplicate_signup():
    # Arrange
    activity_name = "Chess Club"
    email = "test-student@mergington.edu"

    # Act - first signup
    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert first signup succeeds
    assert first_response.status_code == 200
    assert "Signed up" in first_response.json()["message"]

    # Act - duplicate signup
    duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert duplicate signup is rejected
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"

    # Cleanup
    cleanup_response = client.delete(f"/activities/{activity_name}/participants?email={email}")
    assert cleanup_response.status_code == 200


def test_remove_participant_unsubscribes_student():
    # Arrange
    activity_name = "Programming Class"
    email = "cleanup-student@mergington.edu"

    # Act - signup the student first
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200

    # Act - remove the participant
    remove_response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert remove_response.status_code == 200
    assert "Unregistered" in remove_response.json()["message"]


def test_remove_non_registered_participant_returns_400():
    # Arrange
    activity_name = "Soccer Team"
    email = "missing-student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_from_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
