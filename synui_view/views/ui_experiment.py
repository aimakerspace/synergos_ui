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
from views.renderer import ExperimentRenderer
from views.utils import (
    is_request_successful,
    render_id_generator,
    render_orchestrator_inputs,
    render_upstream_hierarchy,
    render_confirmation_form,
    render_experiments,
    render_runs,
    MultiApp
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create new experiment(s)",
    "Browse existing experiment(s)",
    "Update existing experiment(s)",
    "Remove existing experiment(s)"
]

R_TYPE = "experiment"

expt_renderer = ExperimentRenderer()

###########
# Helpers #
###########


###################################################
# Experiment UI Option - Create new Experiment(s) #
###################################################

def create_experiments(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the creation of projects within a specified
        Synergos network
    """
    st.title("Orchestrator - Create New Experiment(s)")

    ########################
    # Step 0: Introduction #
    ########################


    #############################################
    # Step 1: Declare all experiment parameters #
    #############################################
    
    st.header("Step 1: Declare your experiment parameters")
    with st.beta_container():
        expt_id = render_id_generator(r_type=R_TYPE)
        architecture = expt_renderer.render_upload_mods()

    ###############################
    # Step 2: Register experiment #
    ###############################

    st.header("Step 2: Submit your experiment entry")
    is_confirmed = render_confirmation_form(
        data=architecture,
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:
        create_resp = driver.experiments.create(
            **key, 
            expt_id=expt_id, 
            **architecture
        )
        is_request_successful(create_resp)



########################################################
# Experiment UI Option - Browse Existing Experiment(s) #
########################################################

def browse_experiments(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the browsing of projects within a specified 
        Synergos network
    """
    st.title("Orchestrator - Browse Existing Experiment(s)")

    ########################
    # Step 0: Introduction #
    ########################


    ###################################################################
    # Step 1: Pull experiment information from specified orchestrator #
    ###################################################################

    st.header("Step 1: Select your experiment of interest")
    selected_expt_id, _ = render_experiments(
        driver=driver,
        **key,
        form_type="display"
    )

    ########################################################################
    # Step 2: Pull associations & relationships of specified collaboration #
    ########################################################################

    st.header("Step 2: Explore Relationships & Associations")
    render_runs(driver=driver, **key, expt_id=selected_expt_id)



########################################################
# Experiment UI Option - Update existing Experiment(s) #
########################################################

def update_experiments(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the updating of metadata in a experiment 
        within a specified Synergos network
    """
    st.title("Orchestrator - Update existing Experiment(s)")

    ###################################################################
    # Step 3: Pull experiment information from specified orchestrator #
    ###################################################################

    st.header("Step 1: Modify your experiment of interest")
    selected_expt_id, updated_experiment = render_experiments(
        driver=driver,
        **key,
        form_type="modify"
    )
                
    #############################
    # Step 4: Update experiment #
    #############################

    st.header("Step 2: Submit your updated experiment entry")
    is_confirmed = render_confirmation_form(
        data=updated_experiment,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        update_resp = driver.experiments.update(
            **key,
            expt_id=selected_expt_id,
            **updated_experiment
        )
        is_request_successful(update_resp)



###########################################################
# Experiment UI Option - Remove existing collaboration(s) #
###########################################################

def remove_experiments(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the deletion of metadata in a experiment 
        within a specified Synergos network
    """
    st.title("Orchestrator - Remove existing collaboration(s)")

    ###################################################################
    # Step 1: Pull experiment information from specified orchestrator #
    ###################################################################

    st.header("Step 1: Target your experiment of interest")
    selected_expt_id, retrieved_experiment = render_experiments(
        driver=driver,
        **key,
        form_type="display"
    )
                
    ################################
    # Step 2: Remove collaboration #
    ################################

    st.header("Step 2: Submit removal request for experiment")
    is_confirmed = render_confirmation_form(
        data=retrieved_experiment,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=True    
    )
    if is_confirmed:
        delete_resp = driver.experiments.delete(**key, expt_id=selected_expt_id)
        is_request_successful(delete_resp)


###################################
# Experiment UI - Page Formatting #
###################################

def app(action: str):
    """ Main app orchestrating experiment management procedures """
    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=create_experiments)
    core_app.add_view(title=SUPPORTED_ACTIONS[1], func=browse_experiments)
    core_app.add_view(title=SUPPORTED_ACTIONS[2], func=update_experiments)
    core_app.add_view(title=SUPPORTED_ACTIONS[3], func=remove_experiments)

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