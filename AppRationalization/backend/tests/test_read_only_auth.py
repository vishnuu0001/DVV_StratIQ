from types import SimpleNamespace

from app.services.auth_service import AuthService


def test_restricted_users_are_always_read_only_case_insensitively():
    for username in ("vishnuu", "prasanna", "siva"):
        assert AuthService.is_read_only_user(SimpleNamespace(username=username))
        assert AuthService.is_read_only_user(SimpleNamespace(username=f" {username.title()} "))


def test_other_users_are_not_implicitly_read_only():
    assert not AuthService.is_read_only_user(SimpleNamespace(username="viewer"))
    assert not AuthService.is_read_only_user(None)
