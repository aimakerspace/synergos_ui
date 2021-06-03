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
from synui.renderer import RunRenderer
from synui.utils import (
    rerun,
    render_id_generator,
    render_orchestrator_inputs,
    render_upstream_hierarchy, 
    render_confirmation_form,
    render_runs
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
        driver.runs.create(**key, run_id=run_id, **hyperparameters)
        rerun(f"Run '{run_id}' has been created.")



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

    # st.header("Step 4: Explore Relationships & Associations")



########################################################
# Run UI Option - Update existing Run(s) #
########################################################

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

    st.header("Step 4: Submit your updated run entry")
    is_confirmed = render_confirmation_form(
        data=updated_hyperparameters,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        driver.runs.update(
            **key,
            run_id=selected_run_id,
            **updated_hyperparameters
        )
        rerun(f"Run '{selected_run_id}' has been updated.")



###########################################################
# Run UI Option - Remove existing collaboration(s) #
###########################################################

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
        driver.runs.delete(**key, run_id=selected_run_id)
        rerun(f"Run '{selected_run_id}' has been updated.")
            


############################
# Run UI - Page Formatting #
############################

def app():
    """ Main app orchestrating run management procedures """
    option = st.sidebar.selectbox(
        label='Select action to perform:', 
        options=SUPPORTED_ACTIONS,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    driver = render_orchestrator_inputs()

    combination_key = render_upstream_hierarchy(r_type=R_TYPE, driver=driver)

    if option == SUPPORTED_ACTIONS[0]:
        create_runs(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[1]:
        browse_runs(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[2]:
        update_runs(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[3]:
        remove_runs(driver, combination_key)