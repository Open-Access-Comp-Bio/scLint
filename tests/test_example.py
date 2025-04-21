import pytest

# Import the module or function you want to test
# from scLint.some_module import some_function


# Example fixture: reusable setup for multiple tests
@pytest.fixture
def sample_data():
    return {"input": [1, 2, 3], "expected_sum": 6, "expected_mean": 2}


# Unit test for addition logic (replace with your real function)
def test_sum(sample_data):
    result = sum(sample_data["input"])
    assert (
        result == sample_data["expected_sum"]
    ), f"Expected {sample_data['expected_sum']}, got {result}"


# Example of testing exceptions
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0


# Parameterized test: test same function with multiple inputs
@pytest.mark.parametrize(
    "input_list, expected", [([1, 2, 3], 6), ([0, 0, 0], 0), ([5, 5, 5], 15)]
)
def test_parametrized_sum(input_list, expected):
    assert sum(input_list) == expected


# Mocking (if you later use external APIs or IO)
def test_mocking_example(monkeypatch):
    def mock_return(self):
        return "mocked!"

    # Pretend this is a function you're mocking
    class SomeClass:
        def real_method(self):
            return "real"

    monkeypatch.setattr(SomeClass, "real_method", mock_return)
    obj = SomeClass()
    assert obj.real_method() == "mocked!"

