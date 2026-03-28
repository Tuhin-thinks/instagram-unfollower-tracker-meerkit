from meerkit.app import create_app

_SENSITIVE_KEYS = {
    'csrf_token',
    'session_id',
    'user_id',
    'csrf_token_added_at',
    'session_id_added_at',
}


def _assert_no_sensitive_keys(payload):
    if isinstance(payload, dict):
        for key, value in payload.items():
            assert key not in _SENSITIVE_KEYS
            _assert_no_sensitive_keys(value)
        return
    if isinstance(payload, list):
        for item in payload:
            _assert_no_sensitive_keys(item)


def _raw_instagram_user():
    return {
        'instagram_user_id': 'ig_123',
        'name': 'Primary',
        'username': 'primary_user',
        'csrf_token': 'secret_csrf',
        'session_id': 'secret_session',
        'user_id': 'secret_user_id',
        'csrf_token_added_at': '2026-03-29T10:00:00',
        'session_id_added_at': '2026-03-29T10:00:00',
        'created_at': '2026-03-29T10:00:00',
    }


def test_me_response_sanitizes_sensitive_fields(monkeypatch):
    app = create_app()
    client = app.test_client()

    monkeypatch.setattr(
        'meerkit.routes.auth._current_app_user',
        lambda: ('app_test_user', 'Test User'),
    )
    monkeypatch.setattr(
        'meerkit.routes.auth.auth_service.build_me_payload',
        lambda app_user_id, name: {
            'app_user_id': app_user_id,
            'name': name,
            'instagram_users': [_raw_instagram_user()],
            'active_instagram_user': _raw_instagram_user(),
        },
    )

    response = client.get('/api/auth/me')

    assert response.status_code == 200
    payload = response.get_json()
    _assert_no_sensitive_keys(payload)
    assert payload['active_instagram_user']['instagram_user_id'] == 'ig_123'


def test_instagram_users_list_response_sanitizes_sensitive_fields(monkeypatch):
    app = create_app()
    client = app.test_client()

    monkeypatch.setattr(
        'meerkit.routes.auth._current_app_user',
        lambda: ('app_test_user', 'Test User'),
    )
    monkeypatch.setattr(
        'meerkit.routes.auth.auth_service.get_instagram_users',
        lambda app_user_id: [_raw_instagram_user()],
    )

    response = client.get('/api/auth/instagram-users')

    assert response.status_code == 200
    payload = response.get_json()
    _assert_no_sensitive_keys(payload)
    assert payload[0]['instagram_user_id'] == 'ig_123'


def test_instagram_user_detail_response_sanitizes_sensitive_fields(monkeypatch):
    app = create_app()
    client = app.test_client()

    monkeypatch.setattr(
        'meerkit.routes.auth._current_app_user',
        lambda: ('app_test_user', 'Test User'),
    )
    monkeypatch.setattr(
        'meerkit.routes.auth.auth_service.get_instagram_user',
        lambda app_user_id, instagram_user_id: _raw_instagram_user(),
    )

    response = client.get('/api/auth/instagram-users/ig_123')

    assert response.status_code == 200
    payload = response.get_json()
    _assert_no_sensitive_keys(payload)
    assert payload['name'] == 'Primary'
