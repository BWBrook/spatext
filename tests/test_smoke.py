"""Bootstrap smoke tests for the spatext package."""

from importlib import resources

import spatext


def test_package_exposes_version() -> None:
    assert spatext.__version__ == "0.1.0"


def test_package_marks_itself_as_typed() -> None:
    assert resources.files("spatext").joinpath("py.typed").is_file()
