#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from typing import Dict, List, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 

##################
# Configurations #
##################



########################################################
# Collaboration Renderer Class - CollaborationRenderer #
########################################################

class CollaborationRenderer(BaseRenderer):
    """ Main class responsible for rendering collaboration-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_catalogue_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str]]:
        """ Renders a form capturing existing Synergos Catalogue metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated catalogue metadata (dict)
        """
        catalogue_host = data.get('catalogue_host', "")
        catalogue_port = data.get('catalogue_port', 0)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            updated_catalogue_host = left_column.text_input(
                label=f"Server IP for Synergos Catalogue:",
                value=catalogue_host,
                help=f"Registered server IP where Synergos Catalogue is hosted"
            )
            updated_catalogue_port = right_column.number_input(
                label=f"Server Port for Synergos Catalogue:",
                value=catalogue_port,
                help=f"Registered server port to access Synergos Catalogue"
            )

            st.markdown("---")

        return {
            'catalogue_host': updated_catalogue_host, 
            'catalogue_port': updated_catalogue_port
        }


    def render_logger_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[str, Dict[int, str]]]:
        """ Renders a form capturing existing Synergos Logger metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated logger metadata (dict)
        """
        logger_host = data.get('logger_host', "")
        
        logger_ports = data.get('logger_ports', {})
        sysmetrics_port = logger_ports.get('sysmetrics', 0)
        director_port = logger_ports.get('director', 0)
        ttp_port = logger_ports.get('ttp', 0)
        worker_port = logger_ports.get('worker', 0)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            updated_logger_host = left_column.text_input(
                label=f"Server IP for Synergos Logger:",
                value=logger_host,
                help=f"Registered server IP where Synergos Logger is hosted"
            )

            updated_sysmetric_port = right_column.number_input(
                label=f"Sysmetrics Port for Synergos Logger:",
                value=sysmetrics_port,
                help=f"Registered Sysmetric port to access Synergos Logger"
            )
            updated_director_port = right_column.number_input(
                label=f"Director Port for Synergos Logger:",
                value=director_port,
                help=f"Registered director port to access Synergos Logger"
            )
            updated_ttp_port = right_column.number_input(
                label=f"TTP Port for Synergos Logger:",
                value=ttp_port,
                help=f"Registered TTP port to access Synergos Logger"
            )
            updated_worker_port = right_column.number_input(
                label=f"Worker Port for Synergos Logger:",
                value=worker_port,
                help=f"Registered worker port to access Synergos Logger"
            )

            st.markdown("---")

        return {
            'logger_host': updated_logger_host,
            'logger_ports': {
                'sysmetrics': updated_sysmetric_port,
                'director': updated_director_port,
                'ttp': updated_ttp_port,
                'worker': updated_worker_port
            }
        }


    def render_meter_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str]]:
        """ Renders a form capturing existing Synergos Meter metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated meter metadata (dict)
        """
        meter_host = data.get('meter_host', "")
        meter_port = data.get('meter_port', 0)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            updated_meter_host = left_column.text_input(
                label=f"Server IP for Synergos Meter:",
                value=meter_host,
                help=f"Registered server IP where Synergos Meter is hosted"
            )
            updated_meter_port = right_column.number_input(
                label=f"Server Port for Synergos Meter:",
                value=meter_port,
                help=f"Registered server port to access Synergos Meter"
            )

            st.markdown("---")

        return {
            'meter_host': updated_meter_host,
            'meter_port': updated_meter_port
        }
        

    def render_mlops_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str]]:
        """ Renders a form capturing existing Synergos MLOps metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated MLOps metadata (dict)
        """
        mlops_host = data.get('mlops_host', "")
        mlops_port = data.get('mlops_port', 0)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            updated_mlops_host = left_column.text_input(
                label=f"Server IP for Synergos MLOps:",
                value=mlops_host,
                help=f"Registered server IP where Synergos MLOps is hosted"
            )
            updated_mlops_port = right_column.number_input(
                label=f"Server Port for Synergos MLOps:",
                value=mlops_port,
                help=f"Registered server port to access Synergos MLOps"
            )

            st.markdown("---")

        return {
            'mlops_host': updated_mlops_host,
            'mlops_port': updated_mlops_port
        }


    def render_mq_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str]]:
        """ Renders a form capturing existing Synergos MQ metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated MQ metadata (dict)
        """
        mq_host = data.get('mq_host', "")
        mq_port = data.get('mq_port', 0)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            updated_mq_host = left_column.text_input(
                label=f"Server IP for Synergos MQ:",
                value=mq_host,
                help=f"Registered server IP where Synergos MQ is hosted"
            )
            updated_mq_port = right_column.number_input(
                label=f"Server Port for Synergos MQ:",
                value=mq_port,
                help=f"Registered server port to access Synergos MQ"
            )

            st.markdown("---")

        return {
            'mq_host': updated_mq_host,
            'mq_port': updated_mq_port
        }


    def render_ui_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str]]:
        """ Renders a form capturing existing Synergos UI metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated UI metadata (dict)
        """
        ui_host = data.get('ui_host', "")
        ui_port = data.get('ui_port', 0)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            updated_ui_host = left_column.text_input(
                label=f"Server IP for Synergos UI:",
                value=ui_host,
                help=f"Registered server IP where Synergos UI is hosted"
            )
            updated_ui_port = right_column.number_input(
                label=f"Server Port for Synergos UI:",
                value=ui_port,
                help=f"Registered server port to access Synergos UI"
            )

            st.markdown("---")

        return {
            'ui_host': updated_ui_host,
            'ui_port': updated_ui_port
        }

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str, Dict[int, str]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registered collaboration.

        Args:
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated collaboration info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=False)

        st.header("Collaboration Components")
        udpated_catalogue = self.render_catalogue_metadata(data)
        updated_logger = self.render_logger_metadata(data)
        updated_meter = self.render_meter_metadata(data)
        updated_mlops = self.render_mlops_metadata(data)
        updated_mq = self.render_mq_metadata(data)
        updated_ui = self.render_ui_metadata(data)

        return {
            **udpated_catalogue, 
            **updated_logger,
            **updated_meter,
            **updated_mlops,
            **updated_mq,
            **updated_ui
        }
