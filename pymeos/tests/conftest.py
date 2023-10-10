from pymeos import pymeos_initialize, pymeos_finalize


def pytest_configure(config):
    pymeos_initialize('UTC')


def pytest_unconfigure(config):
    pymeos_finalize()


class TestPyMEOS:
    pass
