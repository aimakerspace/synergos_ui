#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import uuid
from typing import Dict, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 

##################
# Configurations #
##################


######################################################
# Registration Renderer Class - RegistrationRenderer #
######################################################

class RegistrationRenderer(BaseRenderer):
    """ Main class responsible for rendering registration-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_registration_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, Union[int, str, bool]]]:
        """ Renders a form capturing existing nodes registered for use 
            under by a participant in a deployed Synergos network, given its 
            prerequisite information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Updated registration (dict)
        """       
        node_details = {
            reg_key: reg_value
            for reg_key, reg_value in data.items()
            if "node_" in reg_key 
        }

        updated_nodes = {}
        for node_idx, node_info in sorted(
            node_details.items(), 
            key=lambda x: x[0]
        ):
            host = node_info.get('host', "")
            rpc_port = node_info.get('f_port', "")
            syft_port = node_info.get('port', "")
            log_msgs = node_info.get('log_msgs', False)
            verbose = node_info.get("verbose", False)

            node_name = " ".join(node_idx.capitalize().split('_'))
            
            with st.beta_container():

                st.header(node_name)

                updated_host = st.text_input(
                    label="IP Address:", 
                    value=host, 
                    key=uuid.uuid4()
                )
                updated_rpc_port = st.text_input(
                    label="RPC Port:", 
                    value=rpc_port, 
                    key=uuid.uuid4()
                )
                updated_syft_port = st.text_input(
                    label="Syft Port:", 
                    value=syft_port, 
                    key=uuid.uuid4()
                )

                log_msgs = st.checkbox(
                    label=f"{node_name}: Display logs", 
                    value=log_msgs
                )

                if log_msgs:
                    verbose = st.checkbox(
                        label=f"{node_name}: Use verbose view", 
                        value=verbose
                    )

            updated_nodes[node_idx] = {
                'host': updated_host,
                'f_port': updated_rpc_port,
                'port': updated_syft_port,
                'log_msgs': log_msgs,
                'verbose': verbose
            }

        return updated_nodes

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, Union[int, str, bool]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registration entry.

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Updated registration info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=True)
        updated_nodes = self.render_registration_metadata(data)

        return updated_nodes