#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from typing import Dict

# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.renderer import CollaborationRenderer
from views.utils import (
    download_button,
    rerun,
    render_orchestrator_inputs,
    render_upstream_hierarchy,
    render_cascading_filter,
    render_participant,
    render_participant_registrations
)

##################
# Configurations #
##################



#############################################################
# Analysis UI Option - Browse and monitor distributed setup #
#############################################################

def commence_analysis(driver: Driver = None, filters: Dict[str, str] = {}):
    """
    """
    st.title("Orchestrator - Analyse your Setup")

    # Extract individual keys
    filtered_collab_id = filters.get('collab_id', None)
    filtered_project_id = filters.get('project_id', None)
    filtered_expt_id = filters.get('expt_id', None)
    filtered_run_id = filters.get('run_id', None)  

    if driver:
        collab_data = driver.collaborations.read(filtered_collab_id).get('data', [])
    else:
        collab_data = {}

    st.write(collab_data)

    st.multiselect(
        label="Detected components:",
        options=[]
    )


#################################
# Analysis UI - Page Formatting #
#################################

def app():
    """ Main app orchestrating collaboration management procedures """

    driver = render_orchestrator_inputs()

    combination_key = render_upstream_hierarchy(r_type="model", driver=driver)

    commence_analysis(driver, combination_key)