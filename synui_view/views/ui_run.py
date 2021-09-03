#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import uuid
from typing import Dict

# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.renderer import RunRenderer
from views.utils import (
    is_request_successful,
    rerun,
    render_id_generator,
    render_orchestrator_inputs,
    render_upstream_hierarchy, 
    render_confirmation_form,
    render_runs,
    MultiApp
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create new Run(s)",
    "Browse existing Run(s)",
    "Update existing Run(s)",
    "Remove existing Run(s)"
]

R_TYPE = "run"

run_renderer = RunRenderer()

###########
# Helpers #
###########


#####################################
# Run UI Option - Create new Run(s) #
#####################################

def create_runs(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the creation of projects within a specified
        Synergos network
    """
    st.title("Orchestrator - Create New Run(s)")

    ########################
    # Step 0: Introduction #
    ########################

    ######################################
    # Step 1: Declare all run parameters #
    ######################################
    
    st.header("Step 1: Declare your hyperparameters")
    with st.beta_container():
        run_id = render_id_generator(r_type=R_TYPE)
        hyperparameters = run_renderer.render_upload_mods()

    ########################
    # Step 2: Register run #
    ########################

    st.header("Step 2: Submit your run entry")
    is_confirmed = render_confirmation_form(
        data=hyperparameters,
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:
        create_resp = driver.runs.create(**key, run_id=run_id, **hyperparameters)
        is_request_successful(create_resp)



##########################################
# Run UI Option - Browse Existing Run(s) #
##########################################

def browse_runs(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the browsing of projects within a specified 
        Synergos network
    """
    st.title("Orchestrator - Browse Existing Run(s)")

    ########################
    # Step 0: Introduction #
    ########################


    ############################################################
    # Step 1: Pull run information from specified orchestrator #
    ############################################################

    st.header("Step 1: Select your run of interest")
    selected_run_id, _ = render_runs(driver=driver, **key, form_type="display")

    ########################################################################
    # Step 2: Pull associations & relationships of specified collaboration #
    ########################################################################

    # st.header("Step 2: Explore Relationships & Associations")



##########################################
# Run UI Option - Update existing Run(s) #
##########################################

def update_runs(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the updating of metadata in a run 
        within a specified Synergos network
    """
    st.title("Orchestrator - Update existing Run(s)")

    ############################################################
    # Step 1: Pull run information from specified orchestrator #
    ############################################################

    st.header("Step 1: Modify your run of interest")
    selected_run_id, updated_hyperparameters = render_runs(
        driver=driver,
        **key,
        form_type="modify"
    )
                
    ######################
    # Step 2: Update run #
    ######################

    st.header("Step 2: Submit your updated run entry")
    is_confirmed = render_confirmation_form(
        data=updated_hyperparameters,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        update_resp = driver.runs.update(
            **key,
            run_id=selected_run_id,
            **updated_hyperparameters
        )
        is_request_successful(update_resp)



####################################################
# Run UI Option - Remove existing collaboration(s) #
####################################################

def remove_runs(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the deletion of metadata in a run 
        within a specified Synergos network
    """
    st.title("Orchestrator - Remove existing collaboration(s)")

    ############################################################
    # Step 1: Pull run information from specified orchestrator #
    ############################################################

    st.header("Step 1: Target your run of interest")
    selected_run_id, updated_hyperparameters = render_runs(
        driver=driver,
        **key,
        form_type="display"
    )            
                
    ################################
    # Step 2: Remove collaboration #
    ################################

    st.header("Step 2: Submit removal request for run")
    is_confirmed = render_confirmation_form(
        data=updated_hyperparameters,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=True    
    )
    if is_confirmed:
        delete_resp = driver.runs.delete(**key, run_id=selected_run_id)
        is_request_successful(delete_resp)
            


############################
# Run UI - Page Formatting #
############################

def app(action: str):
    """ Main app orchestrating run management procedures """
    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=create_runs)
    core_app.add_view(title=SUPPORTED_ACTIONS[1], func=browse_runs)
    core_app.add_view(title=SUPPORTED_ACTIONS[2], func=update_runs)
    core_app.add_view(title=SUPPORTED_ACTIONS[3], func=remove_runs)

    driver = render_orchestrator_inputs()

    if driver:
        combination_key = render_upstream_hierarchy(r_type=R_TYPE, driver=driver)
        core_app.run(action)(driver, combination_key)

    else:
        st.warning(
            """
            Please declare a valid grid connection to continue.
            
            You will see this message if:

                1. You have not declared your grid in the sidebar
                2. Connection parameters you have declared are invalid
            """
        )