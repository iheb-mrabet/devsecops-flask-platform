import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    test_app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test_platform.db"),
            "SECRET_KEY": "test-secret",
        }
    )

    with test_app.test_client() as test_client:
        yield test_client


def test_home_page(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Recruitment security lab" in body
    assert "DevSecOps Jobs" in body


def test_login_page(client):
    response = client.get("/login")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Login" in body
    assert "admin123" in body


def test_dashboard_access_after_login(client):
    login_response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )

    assert login_response.status_code == 200
    assert "Recruitment overview" in login_response.get_data(as_text=True)

    dashboard_response = client.get("/dashboard")
    dashboard_body = dashboard_response.get_data(as_text=True)

    assert dashboard_response.status_code == 200
    assert "Open jobs" in dashboard_body


def test_search_page_reflects_query(client):
    payload = "<script>alert(1)</script>"
    response = client.get("/search", query_string={"q": payload})
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert payload in body
    assert "Showing results for" in body


def test_feedback_submission_is_stored(client):
    payload = "<script>alert('stored')</script>"
    response = client.post(
        "/feedback",
        data={
            "name": "Security Tester",
            "email": "tester@example.test",
            "message": payload,
        },
        follow_redirects=True,
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Feedback submitted" in body
    assert payload in body
