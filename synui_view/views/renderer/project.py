#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import pprint
from typing import Dict, List, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 

##################
# Configurations #
##################

SUPPORTED_ML_OPERATIONS = [
    "regress", 
    "classify"
    # "cluster",
    # "associate"
]

############################################
# Project Renderer Class - ProjectRenderer #
############################################

class ProjectRenderer(BaseRenderer):
    """ Main class responsible for rendering project-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_action_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, str]:
        """ Renders a form capturing existing the machine learning 
            action/operation metadata to be undertaken for a specified project
            registered in a deployed Synergos network, given its prerequisite 
            project information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered project
        Returns:
            Updated action (dict)
        """
        action = data.get('action', SUPPORTED_ML_OPERATIONS[0])
        action_idx = SUPPORTED_ML_OPERATIONS.index(action)

        with st.beta_container():

            updated_action = st.selectbox(
                label="Action:",
                index=action_idx,
                options=SUPPORTED_ML_OPERATIONS,
                help="Type of ML action to perform on the dataset pool"
            )
            
            st.markdown("---")

        return {'action': updated_action}


    def render_incentives_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, List[Any]]]:
        """ Renders a form capturing existing the incentive tierings to be
            adopted for a specified project registered in a deployed Synergos 
            network, given its prerequisite project information, as well as any
            updates to their values.

        Args:
            data (dict): Information relevant to a registered project
        Returns:
            Updated incentives (dict)
        """
        incentives = data.get('incentives', {})

        with st.beta_container():
            columns = st.beta_columns(2)

            tier_count = columns[0].number_input(
                label="Incentive tiers:",
                min_value=0,
                value=len(incentives)
            )

            updated_incentives = {
                f'tier{tier_idx}': incentives.get(f'tier{tier_idx}', [])
                for tier_idx in range(1, tier_count+1)
            }

            columns[1].text_area(
                label="Preview:",
                value=updated_incentives,
                height=200,
                help="Incentive hierarchy to be applied on the project"
            )

            st.markdown("---")

        return {'incentives': updated_incentives}

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[str, Dict[str, List[Any]]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registered project.

        Args:
            data (dict): Information relevant to a registered project
        Returns:
            Updated project info (dict)
        """
        if not data:
            return {}
            
        super().display(data, is_stacked=False)

        st.header("Project Metadata")
        with st.beta_container():
            updated_action = self.render_action_metadata(data)
            updated_incentives = self.render_incentives_metadata(data)

        return {**updated_action, **updated_incentives}
