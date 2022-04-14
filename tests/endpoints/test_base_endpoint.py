from dataclasses import dataclass
from e621.endpoints.endpoints import BaseEndpoint
from e621.api import E621API


def test_argument_validation_switch():
    class TestEndpoint(BaseEndpoint, validate_args=True):
        def some_method(self, a: int):
            pass

    TestEndpoint(E621API(validate_input=False))
