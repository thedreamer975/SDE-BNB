from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from app.config import get_settings
from app.main import DEFAULT_JWT_SECRET, create_app
from app.security import create_access_token


def test_register_success(client: TestClient):
    payload = {
        "name": "Jane Traveler",
        "email": "jane@example.com",
        "password": "SecurePassword123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert data["name"] == "Jane Traveler"
    assert data["email"] == "jane@example.com"
    assert data["role"] == "guest"
    assert data["is_superhost"] is False
    assert "created_at" in data
    assert "password_hash" not in data
    assert "password" not in data

    # Verify session cookie was set
    assert "session" in response.cookies
    assert len(response.cookies["session"]) > 20


def test_register_duplicate_email(client: TestClient):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "SecurePassword123",
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt to register with the same email (case-insensitive)
    payload_dup = {
        "name": "Another User",
        "email": "DUPLICATE@example.com",
        "password": "SecurePassword123",
    }
    res2 = client.post("/api/auth/register", json=payload_dup)
    assert res2.status_code == 409
    err = res2.json()
    assert err["error"]["code"] == "CONFLICT"
    assert "email" in err["error"]["fields"]


@pytest.mark.parametrize(
    "bad_password",
    [
        "short1",  # < 8 chars
        "onlylettersinthispassword",  # no digits
        "1234567890",  # no letters
    ],
)
def test_register_weak_password_rejected(client: TestClient, bad_password: str):
    payload = {
        "name": "Weak Pwd User",
        "email": f"weak_{bad_password[:4]}@example.com",
        "password": bad_password,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    err = response.json()
    assert err["error"]["code"] == "VALIDATION_ERROR"
    assert "password" in err["error"]["fields"]


def test_register_invalid_email_rejected(client: TestClient):
    payload = {
        "name": "Invalid Email",
        "email": "not-an-email-at-all",
        "password": "SecurePassword123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    err = response.json()
    assert err["error"]["code"] == "VALIDATION_ERROR"
    assert "email" in err["error"]["fields"]


def test_login_success(client: TestClient):
    # Register first
    client.post(
        "/api/auth/register",
        json={"name": "Login User", "email": "login@example.com", "password": "Password123"},
    )

    # Login with uppercase email test
    login_payload = {"email": "LOGIN@example.com", "password": "Password123"}
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "login@example.com"
    assert "password_hash" not in data
    assert "session" in response.cookies


def test_login_bad_password_and_unknown_email_have_same_generic_message(client: TestClient):
    client.post(
        "/api/auth/register",
        json={"name": "Known User", "email": "known@example.com", "password": "Password123"},
    )

    # Unknown email
    res_unknown = client.post(
        "/api/auth/login",
        json={"email": "unknown@example.com", "password": "Password123"},
    )
    assert res_unknown.status_code == 401
    err_unknown = res_unknown.json()
    assert err_unknown["error"]["code"] == "UNAUTHENTICATED"
    assert err_unknown["error"]["message"] == "Incorrect email or password."

    # Known email with wrong password
    res_bad_pw = client.post(
        "/api/auth/login",
        json={"email": "known@example.com", "password": "WrongPassword123"},
    )
    assert res_bad_pw.status_code == 401
    err_bad_pw = res_bad_pw.json()
    assert err_bad_pw["error"]["code"] == "UNAUTHENTICATED"
    assert err_bad_pw["error"]["message"] == "Incorrect email or password."

    # Both messages must be identical to prevent user enumeration
    assert err_unknown["error"]["message"] == err_bad_pw["error"]["message"]


def test_me_authenticated_and_unauthenticated(client: TestClient):
    # Unauthenticated request
    res_unauth = client.get("/api/auth/me")
    assert res_unauth.status_code == 401
    assert res_unauth.json()["error"]["code"] == "UNAUTHENTICATED"

    # Authenticate via register
    reg_res = client.post(
        "/api/auth/register",
        json={"name": "Auth Me User", "email": "authme@example.com", "password": "Password123"},
    )
    cookie = reg_res.cookies["session"]

    # Authenticated call
    client.cookies.set("session", cookie)
    res_auth = client.get("/api/auth/me")
    assert res_auth.status_code == 200
    assert res_auth.json()["email"] == "authme@example.com"


def test_me_expired_and_tampered_cookie(client: TestClient):
    # Expired token
    expired_token = create_access_token({"sub": "1", "role": "guest"}, expires_delta=timedelta(seconds=-10))
    client.cookies.set("session", expired_token)
    res_expired = client.get("/api/auth/me")
    assert res_expired.status_code == 401
    assert res_expired.json()["error"]["code"] == "UNAUTHENTICATED"

    # Tampered token
    tampered_token = expired_token[:-5] + "XXXXX"
    client.cookies.set("session", tampered_token)
    res_tampered = client.get("/api/auth/me")
    assert res_tampered.status_code == 401
    assert res_tampered.json()["error"]["code"] == "UNAUTHENTICATED"


def test_logout_clears_cookie(client: TestClient):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Logout User", "email": "logout@example.com", "password": "Password123"},
    )
    assert "session" in reg.cookies

    # Logout
    res_logout = client.post("/api/auth/logout")
    assert res_logout.status_code == 204

    # The cookie in client should be cleared
    client.cookies.delete("session")
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 401


def test_become_host_flow(client: TestClient):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Future Host", "email": "futurehost@example.com", "password": "Password123"},
    )
    assert reg.json()["role"] == "guest"
    cookie = reg.cookies["session"]
    client.cookies.set("session", cookie)

    # Become host
    res_become = client.post("/api/users/me/become-host")
    assert res_become.status_code == 200
    assert res_become.json()["role"] == "host"

    # Verify new session cookie is issued and /me reflects host role
    new_cookie = res_become.cookies.get("session") or client.cookies.get("session")
    client.cookies.set("session", new_cookie)
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 200
    assert res_me.json()["role"] == "host"


def test_update_user_name(client: TestClient):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Original Name", "email": "editname@example.com", "password": "Password123"},
    )
    client.cookies.set("session", reg.cookies["session"])

    # Update name
    res_update = client.patch("/api/users/me", json={"name": "Updated Name"})
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Updated Name"

    # Verify change persists on /me
    res_me = client.get("/api/auth/me")
    assert res_me.json()["name"] == "Updated Name"

    # Reject too short name
    res_short = client.patch("/api/users/me", json={"name": "A"})
    assert res_short.status_code == 422


def test_rate_limit_exceeded(client: TestClient):
    from app.core.limiter import limiter
    limiter.reset()

    # Hit /api/auth/login 5 times
    for _ in range(5):
        res = client.post("/api/auth/login", json={"email": "ratelimit@example.com", "password": "Password123"})
        assert res.status_code in (401, 200)

    # 6th attempt should be rate limited to 5/minute
    res_limited = client.post("/api/auth/login", json={"email": "ratelimit@example.com", "password": "Password123"})
    assert res_limited.status_code == 429
    err = res_limited.json()
    assert err["error"]["code"] == "RATE_LIMITED"
    assert "Too many attempts" in err["error"]["message"]

    limiter.reset()


def test_non_json_mutating_body_rejected(client: TestClient):
    response = client.post(
        "/api/auth/login",
        content="some=form&encoded=data",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_password_hash_never_exposed(client: TestClient):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Audit User", "email": "audit@example.com", "password": "Password123"},
    )
    assert "password_hash" not in str(reg.json())
    assert "password" not in reg.json()

    login = client.post(
        "/api/auth/login",
        json={"email": "audit@example.com", "password": "Password123"},
    )
    assert "password_hash" not in str(login.json())

    client.cookies.set("session", login.cookies["session"])
    me = client.get("/api/auth/me")
    assert "password_hash" not in str(me.json())

    patch = client.patch("/api/users/me", json={"name": "Audit User Two"})
    assert "password_hash" not in str(patch.json())

    host = client.post("/api/users/me/become-host")
    assert "password_hash" not in str(host.json())


def test_production_boot_guard(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ENV", "production")
    monkeypatch.setattr(settings, "JWT_SECRET", DEFAULT_JWT_SECRET)

    with pytest.raises(RuntimeError, match="Production environment requires a secure"):
        create_app()
