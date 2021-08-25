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

SUPPORTED_ROLES = ['guest', 'host']

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

    def render_role_declaration(self, data: Dict[str, Any] = {}) -> str:
        """ Renders an input form for participants to declare their respective
            roles within the context of the current project

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Role details (str)
        """
        role = data.get('role', "guest")

        with st.beta_container():
            columns = st.beta_columns((1, 1, 2, 2))

            with columns[0]:
                user_role = st.selectbox(
                    label="Role:",
                    options=SUPPORTED_ROLES,
                    index=SUPPORTED_ROLES.index(role),
                    help="Specify what is your objective in participating in \
                    this project. A guest participates primarily for improving \
                    their models, while a host participates to contribute data."
                )

        return {'role': user_role}


    def render_registration_metadata(
        self,
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, Union[int, str, bool]]]:
        """ Renders an input form for participants to declare their compute
            nodes to be used for a specific project

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Combined Node details (dict)
        """
        MAX_PER_ROW = 5

        n_count = data.get('n_count', 1)

        with st.beta_container():

            columns = st.beta_columns((1, 1, 2, 2))
            node_count = columns[0].number_input(
                label="No. of Compute Nodes:", 
                value=n_count,
                help="Declare no. of compute nodes to register for project. \
                Synergos will auto-scale the training workload across these \
                declared resources."
            )

            with st.beta_container():
                columns = st.beta_columns(min(node_count, MAX_PER_ROW))

                updated_node_details = {}
                for node_idx in range(node_count):
                    
                    col_idx = node_idx % MAX_PER_ROW

                    node_info = data.get(f'node_{node_idx}', {})
                    curr_host = node_info.get('host', "")
                    curr_rpc_port = node_info.get('f_port', 5000)
                    curr_syft_port = node_info.get('port', 8020)
                    curr_log_msgs = node_info.get('log_msgs', False)
                    curr_verbose = node_info.get("verbose", False)
    
                    with columns[col_idx]:

                        node_name = f"Node {node_idx}"
                        st.header(node_name)

                        with st.beta_container():

                            updated_input_host = st.text_input(
                                label="IP Address:", 
                                value=curr_host,
                                key=node_name
                            )
                            updated_input_rpc_port = st.number_input(
                                label="RPC Port:",
                                value=curr_rpc_port,
                                key=node_name
                            )
                            updated_input_syft_port = st.number_input(
                                label="Syft Port:",
                                value=curr_syft_port,
                                key=node_name
                            )

                            updated_log_msgs = st.checkbox(
                                label=f"{node_name} - Display logs",
                                value=curr_log_msgs,
                                key=node_name
                            )

                            updated_verbose = curr_verbose
                            if updated_log_msgs:
                                verbose = st.checkbox(
                                    label=f"{node_name} - Use verbose view",
                                    value=verbose,
                                    key=node_name
                                )
                    
                            updated_node_details[f"node_{node_idx}"] = {
                                'host': updated_input_host,
                                'f_port': updated_input_rpc_port,
                                'port': updated_input_syft_port,
                                'log_msgs': updated_log_msgs,
                                'verbose': updated_verbose
                            }

                            st.markdown("---")

        return {'nodes': updated_node_details}


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

        super().display(data, is_stacked=False)

        updated_role = self.render_role_declaration(data)
        updated_nodes = self.render_registration_metadata(data)


        return {**updated_role, **updated_nodes}
