#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import base64
import os
import json
import pickle
import uuid
import re
from typing import Dict, List

# Libs
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Custom
import synergos
# from synui.orchestrator_ops import 
from synui.utils import download_button

##################
# Configurations #
##################



########################################
# Base Provision Class - BaseProvision #
########################################

class BaseProvision:
    """
    """
    
    def __init__(self) -> None:
        self.sites = {}
    
    ###########
    # Setters #
    ###########

    def add_site(self, purpose: str, host: str, ports: Dict[int, int]):
        """ 

        Args:
            purpose (str): Type of component allocated to this server
            host (str): Host IP of the allocated server
            ports (Dict(int)): Port mappings that component service uses
        """
        self.sites[purpose] = {'host': host, 'ports': ports}

    ##################
    # Core Functions #
    ##################

    def compile(self):
        """ Compiles the specified components into a single docker-compose.yml
            file for ease of deployment.

        Returns:
            Path to deployment script (str)
        """
        script_path = "docker-compose.yml"
        for site in self.sites.items():
            pass

        return script_path



########################################################
# Orchestrator Provision Class - OrchestratorProvision #
########################################################

class OrchestratorProvision(BaseProvision):
    """
    """
    
    def __init__(self, mode: str = "local") -> None:
        self._INTERNAL_PORTS = {
            'director': {
                'port': 5000
            },
            'ttp': {
                'f_port': 5000,
                'ws_port': 8020
            },
            'catalogue': {
                'catalogue_ui_port': 5000,
                'catalogue_search_port': 5000,
                'catalogue_meta_port': 5000,
                'es_port': 9200,
                'db_ui_port': 7474,
                'db_search_port': 7687
            },
            'logger': {
                'logger_ui_port': 9000,
                'sysmetrics_port': 9100,
                'director_port': 9200,
                'ttp_port': 9300,
                'worker_port': 9400
            },
            'meter': {
                'port': 7000    # arbitrarily set for now
            },
            'mlops': {
                'port': 7000    # arbitrarily set for now
            },
            'mq': {
                'mq_ui_port': 15672,
                'mq_ops_port': 5672
            },
            'ui': {
                'ui_port': 8080,
                'ui_nav_port': 12345,
                'nginx_port': 80,
            }
        }
        self.mode = mode
        super().__init__()

    ###########
    # Setters #
    ###########

    def add_director(self, host: str, port: int = 4000):
        """
        """
        pass


    def add_ttp(self, host: str, port: int = 5000):
        """
        """
        pass


    def add_catalogue(
        self, 
        host: str, 
        catalogue_ui_port: int = 6000,
        catalogue_search_port: int = 6001,
        catalogue_meta_port: int = 6002,
        es_port: int = 6003,
        db_ui_port: int = 6004,
        db_search_port: int = 6005
    ):
        """ Declares server hosting Synergos Catalogue.

        Args:
            host (str): Host IP of the allocated server
            catalogue_ui_port (int): Port for main catalogue UI
            catalogue_search_port (int): Port for internal catalogue search API 
            catalogue_meta_port (int): Port for interal catalogue metadata API
            es_port (int): Port for catalogue's ElasticSearch module
            db_ui_port (int): Port for catalogue's database UI
            db_search_port (int): Port for catalogue's database query API
        """
        catalogue_ports = self._INTERNAL_PORTS['catalogue']
        super().add_site(
            purpose="catalogue", 
            host=host, 
            ports={
                catalogue_ports['catalogue_ui_port']: catalogue_ui_port, 
                catalogue_ports['catalogue_search_port']: catalogue_search_port,
                catalogue_ports['catalogue_meta_port']: catalogue_meta_port,
                catalogue_ports['es_port']: es_port,
                catalogue_ports['db_ui_port']: db_ui_port,
                catalogue_ports['db_search_port']: db_search_port
            }
        )
        

    def add_logger(
        self, 
        host: str,
        logger_ui_port: int = 9000,
        sysmetrics_port: int = 9100,
        director_port: int = 9200,
        ttp_port: int = 9300,
        worker_port: int = 9400
    ):
        """ Declares server hosting Synergos Logger.

        Args:
            host (str): Host IP of the allocated server
            logger_ui_port (int): Port for main logger UI
            sysmetrics_port (int): Port for ingesting system logs 
            director_port (int): Port for ingesting director-related logs
            ttp_port (int): Port for ingesting TTP-related logs
            worker_port (int): Port for ingesting worker-related logs
        """
        logger_ports = self._INTERNAL_PORTS['logger']
        super().add_site(
            purpose="logger", 
            host=host, 
            ports={
                logger_ports['logger_ui_port']: logger_ui_port,
                logger_ports['sysmetrics_port']: sysmetrics_port,
                logger_ports['director_port']: director_port,
                logger_ports['ttp_port']: ttp_port,
                logger_ports['worker_port']: worker_port
            }
        )


    def add_meter(self, host: str, port: str):
        """ Declares server hosting Synergos Meter.

        Args:
            host (str): Host IP of the allocated server
            port (int): Port for accessing Synergos Meter services
        """
        meter_ports = self._INTERNAL_PORTS['meter']
        super().add_site(
            purpose="meter", 
            host=host, 
            ports={
                meter_ports['port']: port,
            }
        )


    def add_mlops(self, host: str, port: str):
        """ Declares server hosting Synergos MLOps.

        Args:
            host (str): Host IP of the allocated server
            port (int): Port for accessing Synergos Meter services
        """
        mlops_ports = self._INTERNAL_PORTS['mlops']
        super().add_site(
            purpose="mlops", 
            host=host, 
            ports={
                mlops_ports['port']: port,
            }
        )


    def configure_mq(
        self, 
        host: str, 
        mq_ui_port: int = 15672,
        mq_ops_port: str = 5672
    ):
        """ Declares server hosting Synergos Meter.

        Args:
            host (str): Host IP of the allocated server
            mq_ui_port (int): Port for main message queue UI/dashboard
            mq_ops_port (int): Port for accessing message queue services/API
        """
        mq_ports = self._INTERNAL_PORTS['mq']
        super().add_site(
            purpose="mq", 
            host=host, 
            ports={
                mq_ports['mq_ui_port']: mq_ui_port,
                mq_ports['mq_ops_port']: mq_ops_port,
            }
        )


    def configure_ui(
        self, 
        host: str, 
        ui_port: int,
        ui_nav_port: int,
        nginx_port: int
    ):
        """ Declares server hosting Synergos Meter.

        Args:
            host (str): Host IP of the allocated server
            ui_port (int): Port for accessing unified UI component
            ui_nav_port (int): Port for accessing filtering nav API
            nginx_port (int): Port for accessing NGINX routing
        """
        ui_ports = self._INTERNAL_PORTS['ui']
        super().add_site(
            purpose="ui", 
            host=host, 
            ports={
                ui_ports['ui_port']: ui_port,
                ui_ports['ui_nav_port']: ui_nav_port,
                ui_ports['nginx_port']: nginx_port,
            }
        )

    ###########
    # Helpers #
    ###########

    def parse_catalogue(self):
        """
        """
        pass


    def 

    ##################
    # Core Functions #
    ##################




######################################################
# Participant Provision Class - ParticipantProvision #
######################################################

class ParticipantProvision(BaseProvision):
    """
    """
    
    def __init__(self) -> None:
        super().__init__()


    def add_site(self):
        """
        """
        pass

    ##################
    # Core Functions #
    ##################
    





################################################
# Orchestrator Provision App - Page Formatting #
################################################



###############################################
# Participant Provision App - Page Formatting #
###############################################