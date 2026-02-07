from hello import add, hello


def test_hello_default():
    assert hello() == "Hello, world!"


def test_hello_name():
    assert hello("Sam") == "Hello, Sam!"


def test_add():
    assert add(2, 3) == 5
