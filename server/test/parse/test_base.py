from src.parse.base import ParsedToken


def test_token_hashing() -> None:
    # Given
    t1 = ParsedToken("In", "in", True)
    t2 = ParsedToken("in", "in", True)

    # When
    bob = {t1, t2}

    # Then
    assert len(bob) == 1

