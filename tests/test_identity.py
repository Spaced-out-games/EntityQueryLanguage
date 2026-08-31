from config import LANGUAGE_NAME, VERSION


def test_identity_is_customized():
    assert "TODO" not in LANGUAGE_NAME
    assert VERSION == "0.1"
