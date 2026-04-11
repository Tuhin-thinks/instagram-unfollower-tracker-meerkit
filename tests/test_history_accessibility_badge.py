from datetime import datetime, timedelta

from meerkit.routes import history


def test_enrich_diff_marks_account_not_accessible_from_task_error(monkeypatch):
    monkeypatch.setattr(
        history._db_service,
        "get_latest_scanned_profile_ids",
        lambda app_user_id, reference_profile_id: set(),
    )
    monkeypatch.setattr(
        history._db_service,
        "get_target_profile",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "target_profile_id": target_profile_id,
            "last_error": None,
        },
    )
    monkeypatch.setattr(
        history._db_service,
        "get_latest_prediction_task",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "status": "error",
            "error": "Could not load this target right now.",
        },
    )
    monkeypatch.setattr(
        history.account_handler,
        "get_alt_followback_assessment_for_target",
        lambda **kwargs: {"is_alt_account_following_you": False},
    )

    diff = {
        "new_followers": [],
        "unfollowers": [
            {
                "pk_id": "123",
                "username": "chatpati_manisha",
            }
        ],
    }

    result = history._enrich_diff_with_alt_followback(
        diff,
        app_user_id="app_user_1",
        reference_profile_id="ig_1",
    )

    assert result is not None
    assert result["unfollowers"][0]["account_not_accessible"] is True


def test_enrich_diff_does_not_mark_accessible_accounts(monkeypatch):
    monkeypatch.setattr(
        history._db_service,
        "get_latest_scanned_profile_ids",
        lambda app_user_id, reference_profile_id: set(),
    )
    monkeypatch.setattr(
        history._db_service,
        "get_target_profile",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "target_profile_id": target_profile_id,
            "last_error": None,
        },
    )
    monkeypatch.setattr(
        history._db_service,
        "get_latest_prediction_task",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "status": "completed",
            "error": None,
        },
    )
    monkeypatch.setattr(
        history.account_handler,
        "get_alt_followback_assessment_for_target",
        lambda **kwargs: {"is_alt_account_following_you": False},
    )

    diff = {
        "new_followers": [],
        "unfollowers": [
            {
                "pk_id": "123",
                "username": "normal_user",
            }
        ],
    }

    result = history._enrich_diff_with_alt_followback(
        diff,
        app_user_id="app_user_1",
        reference_profile_id="ig_1",
    )

    assert result is not None
    assert result["unfollowers"][0]["account_not_accessible"] is False


def test_enrich_diff_prefers_fresh_db_deactivated_status(monkeypatch):
    now = datetime.now().isoformat()
    monkeypatch.setattr(
        history._db_service,
        "get_latest_scanned_profile_ids",
        lambda app_user_id, reference_profile_id: set(),
    )
    monkeypatch.setattr(
        history._db_service,
        "get_target_profile",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "target_profile_id": target_profile_id,
            "is_deactivated": True,
            "update_date": now,
            "last_error": None,
        },
    )
    monkeypatch.setattr(
        history._db_service,
        "get_latest_prediction_task",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "status": "completed",
            "error": None,
        },
    )
    monkeypatch.setattr(
        history.account_handler,
        "get_alt_followback_assessment_for_target",
        lambda **kwargs: {"is_alt_account_following_you": False},
    )

    diff = {
        "new_followers": [],
        "unfollowers": [
            {
                "pk_id": "123",
                "username": "fresh_db_status",
                "account_not_accessible": False,
            }
        ],
    }

    result = history._enrich_diff_with_alt_followback(
        diff,
        app_user_id="app_user_1",
        reference_profile_id="ig_1",
    )

    assert result is not None
    assert result["unfollowers"][0]["account_not_accessible"] is True


def test_enrich_diff_uses_fallback_when_db_status_stale(monkeypatch):
    stale_time = (datetime.now() - timedelta(days=2)).isoformat()
    monkeypatch.setattr(
        history._db_service,
        "get_latest_scanned_profile_ids",
        lambda app_user_id, reference_profile_id: set(),
    )
    monkeypatch.setattr(
        history._db_service,
        "get_target_profile",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "target_profile_id": target_profile_id,
            "is_deactivated": False,
            "update_date": stale_time,
            "last_error": None,
        },
    )
    monkeypatch.setattr(
        history._db_service,
        "get_latest_prediction_task",
        lambda app_user_id, reference_profile_id, target_profile_id: {
            "status": "error",
            "error": "stale fallback should apply",
        },
    )
    monkeypatch.setattr(
        history.account_handler,
        "get_alt_followback_assessment_for_target",
        lambda **kwargs: {"is_alt_account_following_you": False},
    )

    diff = {
        "new_followers": [],
        "unfollowers": [
            {
                "pk_id": "123",
                "username": "stale_db_status",
                "account_not_accessible": False,
            }
        ],
    }

    result = history._enrich_diff_with_alt_followback(
        diff,
        app_user_id="app_user_1",
        reference_profile_id="ig_1",
    )

    assert result is not None
    assert result["unfollowers"][0]["account_not_accessible"] is True
