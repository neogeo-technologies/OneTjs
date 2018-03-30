# -*- coding: utf-8 -*-

import logging
import os
import yaml

from app.models.service import Service

SERVICES_FILE_NAME = "services.yml"


class ServicesManager(object):

    def __init__(self, app):

        self.app = app
        self.services_cfg_file_path = None
        self.services = {}

        # Find the services yaml file
        self.__find_services_yml_file_path()

        # Read the services param file
        with open(self.services_cfg_file_path, 'r') as stream:
            try:
                services_dict = yaml.load(stream)

                for k, v in list(services_dict.items()):
                    v["cfg_file_path"] = self.services_cfg_file_path
                    v["name"] = k
                    s = Service(**v)
                    self.services[k] = s
                    self.app.init_success = True
            except yaml.YAMLError as e:
                logging.exception(e)
                logging.critical("The app config file is not correctly formed. The initialization porcess will stop."
                                 "The following configuration file must be fixed before the application is restarted : "
                                 "{}".format(self.services_cfg_file_path))

    def __find_services_yml_file_path(self):

        config_data_dir_path = self.app.config['DATA_DIR_PATH']
        services_yml_file_path = None

        if os.path.exists(config_data_dir_path):
            services_yml_file_path = self.__find_services_yml_file_in_path(config_data_dir_path)

        if services_yml_file_path is None:
            services_yml_file_path = self.__find_services_yml_file_in_path(
                os.path.join(self.app.root_path, config_data_dir_path))

        self.services_cfg_file_path = services_yml_file_path

    @staticmethod
    def __find_services_yml_file_in_path(dir_path):

        matches = []

        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if f == SERVICES_FILE_NAME:
                    matches.append(os.path.realpath(os.path.join(root, f)))

        if len(matches) > 0:
            return matches[0]

    def get_service_with_name(self, service_name):
        return self.services.get(service_name)

    def get_services(self):
        return list(self.services.values())
