from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from logic.auth_service import AuthService


@pytest.fixture
def repositories():
    user_repository = MagicMock()
    token_repository = MagicMock()
    email_service = MagicMock()
    audit_repository = MagicMock()
    return user_repository, token_repository, email_service, audit_repository


@pytest.fixture
def auth_service(repositories):
    user_repository, token_repository, email_service, audit_repository = repositories
    return AuthService(user_repository, token_repository, email_service, audit_repository)
