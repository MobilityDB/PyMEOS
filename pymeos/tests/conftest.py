import pytest

from pymeos import pymeos_initialize, pymeos_finalize


@pytest.fixture(scope="session", autouse=True)
def setup_meos(request):
    print('Initializing MEOS')
    pymeos_initialize('UTC')
    yield
    pymeos_finalize()


@pytest.mark.usefixtures('setup_meos')
class TestPyMEOS:
    pass


pymeos_initialize('UTC')