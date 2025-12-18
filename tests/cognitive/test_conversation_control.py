from ai_api.conversation_control import decide

def test_repeat_detection():
    d = decide("Repite")
    assert d.kind == "repeat_last"

def test_meta_detection():
    d = decide("¿De qué estamos hablando?")
    assert d.kind == "meta_summary"

def test_normal_message():
    d = decide("Hola, ¿cómo estás?")
    assert d.kind == "normal"
