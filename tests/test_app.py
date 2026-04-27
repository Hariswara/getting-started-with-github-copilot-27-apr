from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def _participants_for(activity_name: str):
    return list(activities[activity_name]["participants"])


def test_get_activities_returns_seeded_data():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert "participants" in payload[expected_activity]


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = "new.player@mergington.edu"
    original = _participants_for(activity_name)
    activities[activity_name]["participants"] = [p for p in original if p != email]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Cleanup shared state for test isolation
    activities[activity_name]["participants"] = original


def test_signup_for_activity_rejects_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_unregister_participant_removes_existing_entry():
    # Arrange
    activity_name = "Debate Team"
    email = "speaker@mergington.edu"
    original = _participants_for(activity_name)
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]

    # Cleanup shared state for test isolation
    activities[activity_name]["participants"] = original


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
