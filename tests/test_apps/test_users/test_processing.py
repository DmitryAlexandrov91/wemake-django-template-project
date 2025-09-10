from typing import Any

import pytest

from server.apps.users.processing import pass_recovery_processing


@pytest.mark.django_db
def test_valid_email_no_user(valid_request: Any) -> None:
    """Tests correct email but no such a user."""
    assert pass_recovery_processing(valid_request) is None
