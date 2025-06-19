"""
Responsible for loading config values from various .properties files into Properties object.
All the config values are loaded by being selective.
"""
from jproperties import Properties

from utils.app_constants import AppConstant


class ConfigParser:
    """
    Provide methods for adding files to load config values from, loading config values at one go
    or by being selective i.e.: loading config values for a specific file only. Moreover, adding
    a new config value, updating an existing one can also be done.
    """

    def __init__(self):
        self.configs = Properties()
        self.files = []

    def add_file(self, file_name):
        self.files.append(file_name)
        return self

    def load_configs(self):
        for file in self.files:
            try:
                with open(file, 'rb') as config_file:
                    temp_config = Properties()
                    temp_config.load(config_file)

                    for __item in temp_config.items():
                        key = __item[0]
                        value = __item[1].data

                        self.set_config(key, value)
            except FileNotFoundError:
                print(f'Sorry, the file {file} does not exists.')

    def load_config(self, config_path=AppConstant.DEV_CONFIG):
        try:
            with open(config_path, 'rb') as config_file:
                self.configs.load(config_file)
        except FileNotFoundError:
            print(f'Sorry, the file {config_path} does not exists.')

    def get_config(self, key):
        value = self.configs.get(key)
        return None if value is None else value.data.strip()

    def set_config(self, key, value):
        self.configs[key] = value

    def delete_config(self, key):
        del self.configs[key]

    def update_config(self, key, value, config_path=AppConstant.DEV_CONFIG):

        with open(config_path, 'wb') as config_file:
            self.configs[key] = value
            self.configs.store(config_file, encoding='utf-8',
                               strip_meta=False, timestamp=False)
