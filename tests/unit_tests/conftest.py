import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    logger.exception = MagicMock()
    return logger

# Optional: attach globally
@pytest.fixture(autouse=True)
def _setup_helpers(request):
    if not hasattr(pytest, "helpers"):
        pytest.helpers = type("Helpers", (), {})
    pytest.helpers.mock_logger = lambda: MagicMock()
