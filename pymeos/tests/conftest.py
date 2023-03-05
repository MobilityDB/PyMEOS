import pytest

from pymeos import pymeos_initialize, pymeos_finalize


@pytest.fixture(scope="session")
def setup_meos(request):
    pymeos_initialize('UTC')
    request.addfinalizer(pymeos_finalize)


@pytest.mark.usefixtures('setup_meos')
class TestPyMEOS:
    pass
