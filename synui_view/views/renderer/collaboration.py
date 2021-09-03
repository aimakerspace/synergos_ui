#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from typing import Dict, List, Union, Any

# Libs
import streamlit as st
from streamlit import logger

# Custom
from config import SUPPORTED_COMPONENTS
from .base import BaseRenderer 

##################
# Configurations #
##################

SUPPORTED_PROTOCOLS = ["HTTP", "HTTPS"]

########################################################
# Collaboration Renderer Class - CollaborationRenderer #
########################################################

class CollaborationRenderer(BaseRenderer):
    """ Main class responsible for rendering collaboration-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()
        self.COMPONENT_OPERATIONS = {
            'catalogue': self.render_catalogue_metadata,
            'logs': self.render_logger_metadata,
            'meter': self.render_meter_metadata,
            'mlops': self.render_mlops_metadata,
            'mq': self.render_mq_metadata
        } 

    ###########
    # Helpers #
    ###########

    def __render_component_metadata(
        self, 
        component: str,
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[int, str]]:
        """ Renders a form capturing existing Synergos Catalogue metadata 
            involved in a deployed Synergos network, given its prerequisite 
            collaboration information, as well as any updates to their values.

        Args:
            component (str): Component to be rendered
            data (dict): Information relevant to a registered collaboration
        Returns:
            Updated catalogue metadata (dict)
        """
        display_name = SUPPORTED_COMPONENTS[component]['name']
        st.subheader(display_name)

        component_info = data.get(component, {})
        component_host = component_info.get('host', "")
        component_main_port = component_info.get('ports', {}).get('main', 0)
        component_ui_port = component_info.get('ports', {}).get('ui', 0)
        component_is_secured = component_info.get('secure', False) 

        with st.beta_container():

            row1_columns = st.beta_columns((1, 4))
            selected_protocol = row1_columns[0].selectbox(
                label="Protocol:",
                options=SUPPORTED_PROTOCOLS,
                index=int(component_is_secured),
                help="Please indicate the security of your connection.",
                key=f"{component}_protocol"
            )
            updated_is_secured = bool(SUPPORTED_PROTOCOLS.index(selected_protocol))
            updated_host = row1_columns[1].text_input(
                label=f"Server IP for Synergos {component.capitalize()}:",
                value=component_host,
                help=f"Registered server IP where Synergos {component.capitalize()} is hosted",
                key=f"{component}_host"
            )

            row2_columns = st.beta_columns(5)
            updated_main_port = row2_columns[1].number_input(
                label=f"Server Port:",
                value=component_main_port,
                help=f"Registered server port to access Synergos {component.capitalize()}",
                key=f"{component}_main"
            )
            updated_ui_port = row2_columns[2].number_input(
                label=f"UI Port:",
                value=component_ui_port,
                help=f"Registered server port to access Synergos {component.capitalize()}",
                key=f"{component}_ui"
            )

        # Only return rendered inputs if they are appropriate values
        if (updated_host and updated_main_port and updated_ui_port):
            updated_info = {
                'host': updated_host,
                'port': updated_main_port,
                'ui_port': updated_ui_port,
                'secure': updated_is_secured
            }
        else:
            updated_info = {}
        
        return updated_info


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
        return self.__render_component_metadata("catalogue", data)


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
        main_info = self.__render_component_metadata("logs", data)

        logger_info = data.get('logs', {})
        logger_sys_port = logger_info.get('ports', {}).get('sysmetrics', 0)
        logger_dir_port = logger_info.get('ports', {}).get('director', 0)
        logger_ttp_port = logger_info.get('ports', {}).get('ttp', 0)
        logger_wrk_port = logger_info.get('ports', {}).get('worker', 0)

        with st.beta_container():

            columns = st.beta_columns(5)
            updated_sysmetric_port = columns[1].number_input(
                label=f"Sysmetrics Port",
                value=logger_sys_port,
                help=f"Registered Sysmetric port to access Synergos Logger",
                key="logs_sysmetrics"
            )
            updated_director_port = columns[2].number_input(
                label=f"Director Port",
                value=logger_dir_port,
                help=f"Registered director port to access Synergos Logger",
                key="logs_director"
            )
            updated_ttp_port = columns[3].number_input(
                label=f"TTP Port",
                value=logger_ttp_port,
                help=f"Registered TTP port to access Synergos Logger",
                key="logs_ttp"
            )
            updated_worker_port = columns[4].number_input(
                label=f"Worker Port",
                value=logger_wrk_port,
                help=f"Registered worker port to access Synergos Logger",
                key="logs_worker"
            )

        # Logger port declarations only take effect if main info is relevant 
        if main_info:
            main_info['sysmetrics_port'] = updated_sysmetric_port
            main_info['director_port'] = updated_director_port
            main_info['ttp_port'] = updated_ttp_port
            main_info['worker_port'] = updated_worker_port

        return main_info


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
        return self.__render_component_metadata("meter", data)


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
        return self.__render_component_metadata('mlops', data)


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
        return self.__render_component_metadata('mq', data)

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

        updated_collab_info = {}
        for component in SUPPORTED_COMPONENTS.keys():
            render_op = self.COMPONENT_OPERATIONS[component]
            updated_collab_info[component] = render_op(data)
            st.markdown("---")

        return updated_collab_info