def detect_errors(expected_text: str, spoken_text: str):
    expected_words = expected_text.lower().split()
    spoken_words = spoken_text.lower().split()

    errors = [word for word in expected_words if word not in spoken_words]
    return errors
