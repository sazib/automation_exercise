# pylint: skip-file
import json

from utils.app_constants import AppConstant


def modify_report_title(allure_report_path, title):
    """
    Update the allure report title with the given name.
    :param summary_json_path: path to the generated 'allure-report'
    """
    with open(f'{AppConstant.PROJECT_ROOT}/{allure_report_path}/widgets/summary.json', 'r+') as summary_file:

        summary_object = json.load(summary_file)
        summary_object['reportName'] = title

        summary_file.seek(0)
        json.dump(summary_object, summary_file, indent=4)
        # summary_file.truncate()
