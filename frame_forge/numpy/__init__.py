import sys
from types import ModuleType


class DummyNumpy(ModuleType):
    """
    This is just a mock numpy to prevent awsmfunc from complaining about
    missing numpy (as we're not using code from awsmfunc that utilizes numpy at all).
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("numpy")


# we'll attempt to import the real numpy and if that fails use the mock numpy
try:
    import numpy

    _ = numpy  # no-op to make it appear "used"
except ImportError:
    sys.modules["numpy"] = DummyNumpy()
