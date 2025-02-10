from uwotm8.convert import convert_american_to_british_spelling


def test_convert_american_to_british_spelling():
    assert convert_american_to_british_spelling("Let's anglicize this text") == "Let's anglicise this text"
