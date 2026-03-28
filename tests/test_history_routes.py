from meerkit.app import create_app
from meerkit.config import HISTORY_ALL_TIME_DAYS, HISTORY_DEFAULT_DAYS, HISTORY_MAX_DAYS


def _patch_active_context(monkeypatch):
    monkeypatch.setattr(
        "meerkit.routes.history.get_active_context",
        lambda instagram_user_id_override=None: (
            "app_test_user",
            {"instagram_user_id": "ig_123"},
        ),
    )


def test_history_defaults_to_recent_with_limit_10(monkeypatch):
    app = create_app()
    client = app.test_client()

    _patch_active_context(monkeypatch)

    captured: dict[str, object] = {}

    def _mock_get_scan_history(
        reference_profile_id: str,
        days: int,
        limit: int,
        offset: int,
    ):
        captured["reference_profile_id"] = reference_profile_id
        captured.update({"days": days, "limit": limit, "offset": offset})
        return []

    monkeypatch.setattr(
        "meerkit.routes.history.get_scan_history",
        _mock_get_scan_history,
    )

    response = client.get("/api/history")

    assert response.status_code == 200
    assert response.get_json() == []
    assert captured == {
        "reference_profile_id": "ig_123",
        "days": HISTORY_DEFAULT_DAYS,
        "limit": 10,
        "offset": 0,
    }


def test_history_all_time_forces_30_days(monkeypatch):
    app = create_app()
    client = app.test_client()

    _patch_active_context(monkeypatch)

    captured: dict[str, object] = {}

    def _mock_get_scan_history(
        reference_profile_id: str,
        days: int,
        limit: int,
        offset: int,
    ):
        captured["reference_profile_id"] = reference_profile_id
        captured.update({"days": days, "limit": limit, "offset": offset})
        return []

    monkeypatch.setattr(
        "meerkit.routes.history.get_scan_history",
        _mock_get_scan_history,
    )

    response = client.get("/api/history?range=all_time&days=2")

    assert response.status_code == 200
    assert captured["days"] == HISTORY_ALL_TIME_DAYS
    assert captured["limit"] == 10
    assert captured["offset"] == 0


def test_history_recent_clamps_days_limit_and_offset(monkeypatch):
    app = create_app()
    client = app.test_client()

    _patch_active_context(monkeypatch)

    captured: dict[str, object] = {}

    def _mock_get_scan_history(
        reference_profile_id: str,
        days: int,
        limit: int,
        offset: int,
    ):
        captured["reference_profile_id"] = reference_profile_id
        captured.update({"days": days, "limit": limit, "offset": offset})
        return []

    monkeypatch.setattr(
        "meerkit.routes.history.get_scan_history",
        _mock_get_scan_history,
    )

    response = client.get("/api/history?range=recent&days=999&limit=999&offset=-5")

    assert response.status_code == 200
    assert captured == {
        "reference_profile_id": "ig_123",
        "days": max(1, HISTORY_MAX_DAYS),
        "limit": 200,
        "offset": 0,
    }


def test_history_invalid_numbers_fall_back_to_defaults(monkeypatch):
    app = create_app()
    client = app.test_client()

    _patch_active_context(monkeypatch)

    captured: dict[str, object] = {}

    def _mock_get_scan_history(
        reference_profile_id: str,
        days: int,
        limit: int,
        offset: int,
    ):
        captured["reference_profile_id"] = reference_profile_id
        captured.update({"days": days, "limit": limit, "offset": offset})
        return []

    monkeypatch.setattr(
        "meerkit.routes.history.get_scan_history",
        _mock_get_scan_history,
    )

    response = client.get("/api/history?range=recent&days=abc&limit=oops&offset=nope")

    assert response.status_code == 200
    assert captured == {
        "reference_profile_id": "ig_123",
        "days": HISTORY_DEFAULT_DAYS,
        "limit": 10,
        "offset": 0,
    }
