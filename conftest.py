"""
Used to set up test configurations and store/modify the testcases that are used
by test functions/methods.
"""

import glob
import json
import os
import re
import shutil
import sys
import logging

import allure
import pytest
from _pytest.mark import Mark, MarkDecorator
from allure_commons.types import AttachmentType
from jproperties import Properties
from playwright.sync_api import sync_playwright, Page

from utils.app_constants import AppConstant
from utils.config_parser import ConfigParser


log = logging.getLogger(__name__)
logging.basicConfig(filename='.automation_exercise_logs.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class Unmarker:
    """
    Return MarkDecorator object.
    """
    def __getattr__(self, item):
        # Return a marker remover
        if item[0] == '_':
            raise AttributeError('Marker name must NOT start with underscore')
        return MarkDecorator(Mark(f'unmark:{item}', args=(), kwargs={}))


class Fauxcals:
    """
    SHould work with the eval() as the set of 'locals'. Will return
    true for any item keyword that begins with unmark. This should only work for
    marks set by 'unmarker', because you can't do `@pytest.mark.namewith:colon`.
    """
    def __init__(self, keywords):
        self.keys = [key.split(':')[1] for key in keywords if 'unmark:' in key]

    def __getitem__(self, item):
        return item in self.keys


@pytest.hookimpl(trylast=True)
def pytest_configure(config):   # pylint: disable=too-many-locals, too-many-statements
    env = config.getoption('--env').lower()
    url = config.getoption('--url')
    browser = config.getoption('--browser')
    marker = config.getoption('-m')
    alluredir = config.getoption('--alluredir') or 'TestResults/allure-reports'

    set_skipped_test(config)

    configs = ConfigParser()

    if env is None or env == 'dev':
        configs.add_file(AppConstant.DEV_CONFIG)
        pytest.conf = AppConstant.DEV_CONFIG
        pytest.env = env
    elif env in ('stage', 'staging'):
        configs.add_file(AppConstant.STAGING_CONFIG)
        pytest.conf = AppConstant.STAGING_CONFIG
        pytest.env = 'staging'
    elif env in ('prod', 'production', 'live'):
        configs.add_file(AppConstant.PRODUCTION_CONFIG)
        pytest.conf = AppConstant.PRODUCTION_CONFIG
        pytest.env = 'prod'
    else:
        sys.exit('Invalid option. Please provide either of the following values:'
                 ' dev, staging, production...')

    configs.add_file(AppConstant.SYSTEM_CONFIG)
    configs.add_file(AppConstant.ALLURE_ENV_FILE)
    configs.add_file(AppConstant.DATA_CONFIG)

    pytest.marker = marker
    configs.load_configs()

    if url is not None:
        configs.set_config('url', url)

    # Other settings is cached here
    pytest.configs = configs
    pytest.browser = browser
    pytest.url = configs.get_config('url')
    pytest.report_title = config.getoption('--report-title')
    pytest.run_skipped = config.getoption('--run-skipped')
    pytest.enable_jenkins = config.getoption('--enable-jenkins')
    pytest.run_locally = config.getoption('--run-locally')
    pytest.alluredir = alluredir
    pytest.unmark = Unmarker()


def pytest_collection_modifyitems(config, items):
    """
    Modifies the collected test cases by adding skip marker. Test case lists are read from
    'skipped_testcases.properties' file under 'resources' folder. Test cases are listed as key
    & associated comments are placed as the value of that particular test case.
    """
    skipped_list = re.split(r'\s+', config.getoption('--skip-list'))

    with open(AppConstant.SKIPPED_TESTCASES_FILE, 'rb') as skipped_tcs_file, \
            open(AppConstant.XFAILED_TESTCASES_FILE, 'rb') as xfailed_tcs_file:

        skipped_config = Properties()
        xfailed_config = Properties()

        skipped_config.load(skipped_tcs_file)
        xfailed_config.load(xfailed_tcs_file)

        skipped_tcs = get_dict_from_loaded_config(skipped_config)
        xfailed_tcs = get_dict_from_loaded_config(xfailed_config)

        ignoring_item_set = set()

    matchexpr = config.option.markexpr

    remaining = []
    deselected = []

    for item in items:
        test_module, _, _ = item.nodeid.split('::')
        test_module_name = test_module.split('/')[-1]
        if test_module_name in skipped_list:
            ignoring_item_set.add(test_module)

            config.__dict__['option'].ignore = list(ignoring_item_set)

        if pytest.run_skipped == 'no':
            add_marker_to_test(item, skipped_tcs, 'skip')
        add_marker_to_test(item, xfailed_tcs, 'xfail')

        # modifying DOCSTRING for each of the test cases in a module/suite.
        test_module_name = '/'.join(item.nodeid.split('::')[0].split('.')[0].split('/')[1:])
        try:
            with open(f'{AppConstant.TEST_STEPS_FOLDER}/{test_module_name}.json',
                      encoding='utf-8') as step_file:
                test_steps_in_json_file = json.load(step_file)

            test_case_steps = test_steps_in_json_file.get(item.obj.__name__, '')
            if isinstance(test_case_steps, list):
                test_case_steps = '\n'.join(test_case_steps)

            setattr(item.obj.__func__, '__doc__', test_case_steps)
        except FileNotFoundError:
            print(f'No such file: {test_module_name}.json.')

        if matchexpr:
            if eval(matchexpr, {}, Fauxcals(item.keywords)):    # pylint: disable=eval-used
                print(f'Deselecting {item!r} (mark removed by @pytest.unmark)')
                deselected.append(item)
                continue
        remaining.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = remaining


def pytest_sessionfinish(session):
    failed_test_list = []
    for item in session.items:
        if hasattr(item, 'rep_call') and item.rep_call.outcome == 'failed':
            failed_test_list.append(item.nodeid.split('::')[0])

    if failed_test_list:
        last_failed_testcases_file = f'{AppConstant.RESOURCE_FOLDER}/' \
                                     f'scp_failed_test_{pytest.marker.upper()}.properties'
        with open(last_failed_testcases_file, 'w', encoding='utf-8'):
            failed_tests_as_arguments = ' '.join(set(failed_test_list))
            configs = ConfigParser()
            configs.update_config('env', pytest.env, config_path=last_failed_testcases_file)
            configs.update_config('url', pytest.url, config_path=last_failed_testcases_file)
            configs.update_config('testtype', pytest.marker,
                                  config_path=last_failed_testcases_file)
            configs.update_config('run_skipped', pytest.run_skipped,
                                  config_path=last_failed_testcases_file)
            configs.update_config('failed_tcs', failed_tests_as_arguments,
                                  config_path=last_failed_testcases_file)


@pytest.fixture(scope='class')
def init_driver(request):
    """
    Initialize driver & yield it to currently running test suite. If any suite uses @pytest.mark.no_auto
    mark then no driver will be returned.
    """
    if 'no_auto' in request.keywords:
        yield
        return

    with sync_playwright() as playwright:
       try:
           browser = getattr(playwright, pytest.browser).launch(headless=False, slow_mo=50, args=['--start-maximized'])
       except AttributeError:
           log.error(f'No such browser \'{pytest.browser}\'. Exiting test execution...\n')
           sys.exit()
       page: Page = browser.new_page()
       page.goto(pytest.url)
       request.cls.page = page

       os.environ['browser_version'] = browser.version

       yield page

       browser.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, 'result', rep)


@pytest.fixture(scope='function', autouse=True)
def failed_page(request):

    yield

    feature_type = request.node.result.when
    feature_outcome = request.node.result.outcome
    print(feature_outcome, '$'*30)
    if feature_outcome == 'failed':
        allure.attach(request.cls.page.screenshot(),
                      name=f'Screenshot for failed {"TESTCASE" if feature_type == "call" else feature_type.upper()}',
                      attachment_type=AttachmentType.JPG)


@pytest.fixture(scope='session', autouse=True)
def update_allure_environment_configs():
    """
    Provides environment specific information if the tests are run on Jenkins.
    """
    yield
    env_configs = ConfigParser()
    # env_configs.update_config('Browser', pytest.browser.title(), AppConstant.ALLURE_ENV_FILE)
    env_configs.update_config('BrowserVersion',
                              str(os.environ.get('browser_version')), AppConstant.ALLURE_ENV_FILE)
    env_configs.update_config('Env', pytest.env.title(), AppConstant.ALLURE_ENV_FILE)
    env_configs.update_config('TestType', pytest.marker.title(), AppConstant.ALLURE_ENV_FILE)
    env_configs.update_config('reportName', 'AutomationExercise TestReport', AppConstant.ALLURE_ENV_FILE)

    os.makedirs(pytest.alluredir, exist_ok=True)

    shutil.copy2(AppConstant.ALLURE_ENV_FILE, pytest.alluredir)


def pytest_addoption(parser):
    parser.addoption('--env', action='store', default='dev', help='env: dev, staging, prod/live or dr')
    parser.addoption('--url', action='store',
                     help='url: dev, staging, production or dr url. If it is provided this value will '
                          'override the value provided by config file.')
    parser.addoption('--browser-version', action='store',
                     help='browser-version: 116/117/118/119/120. Used for selecting '
                          'chrome browser version to execute test cases.')
    parser.addoption('--browser', action='store', default='chrome',
                     help='browser: chrome/firefox/headless-chrome. Used for browser selection,')
    parser.addoption('--repeat', action='store', type=int, default=1, help='Run eah test specified number of times.')
    parser.addoption('--report-title', action='store', default='ScribePortal Automation Report')
    parser.addoption('--run-skipped', action='store', default='no',
                     help='Enable skipped test cases.')
    parser.addoption('--enable-jenkins', action='store', default='no',
                     help='Enable running from local machine/Jenkins.'
                          ' --enable-jenkins=no by default.')
    parser.addoption('--skip-list', action='store', default='', help='Path to module/package to skip.')
    parser.addoption('--run-locally', action='store', default='no',
                     help='Running code locally using either simulator or lambda-test real device.'
                          ' If \'no\' is selected then test will be run on simulator.')


def get_dict_from_loaded_config(testcases_config=None):
    testcase_dict = {}
    for __item in testcases_config.items():
        key = __item[0]
        value = __item[1].data
        testcase_dict[key] = value

    return testcase_dict


def add_marker_to_test(item, marker_info_dict, marker_type='skip'):
    collected_class_name = item.nodeid.split('::')[1]

    if collected_class_name in marker_info_dict:
        expected_marker = prepare_marker(marker_info_dict, collected_class_name, marker_type)
        item.add_marker(expected_marker)
    elif item.name in marker_info_dict:
        expected_marker = prepare_marker(marker_info_dict, item.name, marker_type)
        item.add_marker(expected_marker)


def prepare_marker(marker_info_dict, tc_or_suite_name, marker_type='skip'):
    unwanted_tc_info_list = marker_info_dict[tc_or_suite_name].split('|')

    if len(unwanted_tc_info_list) == 1:
        skip_marker = pytest.mark.skip(reason=unwanted_tc_info_list[0])
        xfail_marker = pytest.mark.xfail(reason=unwanted_tc_info_list[0])
    else:
        skip_marker = pytest.mark.skipif(pytest.env in unwanted_tc_info_list[0].split(','),
                                         reason=unwanted_tc_info_list[1])
        xfail_marker = pytest.mark.xfail(pytest.env in unwanted_tc_info_list[0].split(','),
                                         reason=unwanted_tc_info_list[1])

    if marker_type == 'skip':
        return skip_marker

    return xfail_marker


def get_modules_and_packages(test_root_dir='testcases'):
    package_or_modules = []

    for item in glob.iglob(test_root_dir + '**/*.py', recursive=True):
        package_or_modules.append(item)

    return package_or_modules


def set_skipped_test(config):
    skipped_list = re.split(r'\s+', config.getoption('--skip-list'))
    package_or_modules = get_modules_and_packages()

    items_to_be_skipped = [package_or_module for package_or_module in package_or_modules
                           if any(package_or_module.endswith(skipped_item)
                                  for skipped_item in skipped_list)]

    print(skipped_list, '&&&'*10)
    print(package_or_modules, '***'*10)
    print(config.__dict__['option'].ignore, '^'*20)

    if config.__dict__['option'].ignore:
        config.__dict__['option'].ignore.extend(items_to_be_skipped)
    else:
        config.__dict__['option'].ignore = items_to_be_skipped