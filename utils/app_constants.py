"""
Provides paths for various resource under resource folder.
"""
from os.path import dirname, join


class AppConstant:
    """
    Used for storing constants.
    """
    PROJECT_ROOT = dirname(dirname(__file__))
    RESOURCE_FOLDER = join(PROJECT_ROOT, 'resources')
    RECORDING_FOLDER = join(RESOURCE_FOLDER, 'recordings')
    TEST_DATA_FOLDER = join(RESOURCE_FOLDER, 'test_data')
    TEST_STEPS_FOLDER = join(RESOURCE_FOLDER, 'test_steps')
    SYSTEM_CONFIG = join(RESOURCE_FOLDER, 'system.properties')
    DEV_CONFIG = join(RESOURCE_FOLDER, 'dev.properties')
    STAGING_CONFIG = join(RESOURCE_FOLDER, 'staging.properties')
    PRODUCTION_CONFIG = join(RESOURCE_FOLDER, 'production.properties')
    DATA_CONFIG = join(RESOURCE_FOLDER, 'data.properties')
    SKIPPED_TESTCASES_FILE = join(RESOURCE_FOLDER, 'skipped_testcases.properties')
    XFAILED_TESTCASES_FILE = join(RESOURCE_FOLDER, 'xfailed_testcases.properties')
    ALLURE_ENV_FILE = join(RESOURCE_FOLDER, 'environment.properties')
    DOCKER_COMPOSE_FILE = join(RESOURCE_FOLDER, 'docker-compose.yml')
    DOCKER_COMPOSE_TEMPLATE_FILE = join(RESOURCE_FOLDER, 'docker-compose-template.yml')