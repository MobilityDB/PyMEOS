from pymeos import pymeos_finalize, pymeos_initialize


def pytest_configure(config):
    pymeos_initialize("UTC")


def pytest_unconfigure(config):
    pymeos_finalize()


class TestPyMEOS:
    pass
