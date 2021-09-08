#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
from io import StringIO
from typing import Dict, List, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 

##################
# Configurations #
##################


###############################################
# Optimization Renderer Class - OptimRenderer #
###############################################

class OptimRenderer(BaseRenderer):
    """ Main class responsible for rendering optimization-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_upload_mods(self) -> Dict[str, dict]:
        """ Renders interface facilitating search space declarations for 
            hyperparameter tuning submitted in a Synergos network.

        Returns:
            Search space (dict)
        """
        with st.beta_container():

            uploaded_file = st.file_uploader(
                label="Upload your hyperparameter ranges:",
                type="json",
                help="Provide a parsable JSON file documenting your search space"    
            )

            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                stringio = StringIO(bytes_data.decode("utf-8"))
                hyperparam_string = stringio.read()
                hyperparam_ranges = {"search_space": json.loads(hyperparam_string)}
            
                # Load preview
                with st.beta_expander(label="Search space", expanded=False):
                    st.code(
                        json.dumps(hyperparam_ranges, sort_keys=True, indent=4),
                        language="json"
                    )

            else:
                hyperparam_ranges = {}

        return hyperparam_ranges

        
    def render_tuning_parameters(self) -> Dict[str, Union[float, int, str]]:
        """ Renders interface facilitating tuner configurations for 
            hyperparmeter tuning submitted in a Synergos network

        Returns:
            Tuning parameters (dict)
        """
        with st.beta_container():

            metric = st.selectbox(
                label="Select your metric:",
                options=["accuracy"],
                help="Select a metric to optimize on."
            )

            optimize_mode = st.selectbox(
                label="Direction of optimization:",
                options=["max", "min"],
                help="Specify if you want to maximize or minimize your selected metric."
            )

            trial_concurrency = st.number_input(
                label="No. of concurrent trials:",
                min_value=1,

            )

            max_exec_duration = st.number_input(
                label="Time Budget (in seconds):",
                value=1000,
                help="""State a time budget for each trial. A time budget is a 
                        duration after which a trial is forcefully terminated. 
                     """
            )

            max_trial_num = st.number_input(
                label="Max number of trials:",
                value=10,
                help="State a maximum number of trials to generate."
            )

        return {
            'metric': metric,
            'optimize_mode': optimize_mode,
            'trial_concurrency': trial_concurrency,
            'max_exec_duration': max_exec_duration,
            'max_trial_num': max_trial_num
        }
