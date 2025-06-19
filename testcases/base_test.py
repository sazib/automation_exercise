"""
This class provides other testing classes with required data loaded from config files, initiated
browser, take screenshots upon any test case failure etc.
"""
import pytest


@pytest.mark.usefixtures('init_driver', 'failed_page')
class BaseTest:
    """
    Base class for all test classes.
    """
    configs = pytest.configs
