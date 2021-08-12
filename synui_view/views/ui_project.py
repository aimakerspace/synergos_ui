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
from views.renderer import ProjectRenderer
from views.utils import (
    rerun,
    render_id_generator,
    render_orchestrator_inputs,
    render_upstream_hierarchy,
    render_confirmation_form,
    render_projects,
    render_experiments,
    render_runs,
    render_orchestrator_registrations
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create new project(s)",
    "Browse existing project(s)",
    "Update existing project(s)",
    "Remove existing project(s)"
]

R_TYPE = "project"

project_renderer = ProjectRenderer()

###########
# Helpers #
###########


#############################################
# Project UI Option - Create new Project(s) #
#############################################

def create_projects(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the creation of projects within a specified
        Synergos network
    """
    st.title("Orchestrator - Create New Project(s)")

    ########################
    # Step 0: Introduction #
    ########################


    ##########################################
    # Step 1: Declare all project parameters #
    ##########################################
    
    st.header("Step 1: Declare your project parameters")
    with st.beta_container():
        project_id = render_id_generator(r_type=R_TYPE)
        updated_action = project_renderer.render_action_metadata()
        updated_incentives = project_renderer.render_incentives_metadata()

    ############################
    # Step 2: Register project #
    ############################

    st.header("Step 2: Submit your project entry")
    project_info = {**updated_action, **updated_incentives}
    is_confirmed = render_confirmation_form(
        data=project_info,
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:
        driver.projects.create(**key, project_id=project_id, **project_info)
        rerun(f"Project '{project_id}' has been created.")


##################################################
# Project UI Option - Browse Existing Project(s) #
##################################################

def browse_projects(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the browsing of projects within a specified 
        Synergos network
    """
    st.title("Orchestrator - Browse Existing Project(s)")

    ########################
    # Step 0: Introduction #
    ########################


    ################################################################
    # Step 1: Pull project information from specified orchestrator #
    ################################################################

    st.header("Step 1: Select your project of interest")
    selected_project_id, _ = render_projects(driver=driver, **key)

    ########################################################################
    # Step 2: Pull associations & relationships of specified collaboration #
    ########################################################################

    st.header("Step 2: Explore Relationships & Associations")
    selected_expt_id, _ = render_experiments(
        driver=driver, 
        **key,
        project_id=selected_project_id
    )
    
    render_runs(
        driver=driver, 
        **key,
        project_id=selected_project_id,
        expt_id=selected_expt_id
    )

    ########################################################
    # Step 3: Browse registrations under specified project #
    ########################################################

    st.header("Step 3: Browse Participant Registry")
    render_orchestrator_registrations(
        driver=driver,
        **key,
        project_id=selected_project_id
    )



##################################################
# Project UI Option - Update existing Project(s) #
##################################################

def update_projects(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the updating of metadata in a project 
        within a specified Synergos network
    """
    st.title("Orchestrator - Update existing Project(s)")

    ################################################################
    # Step 1: Pull project information from specified orchestrator #
    ################################################################

    st.header("Step 1: Modify your project of interest")
    selected_project_id, updated_project = render_projects(driver=driver, **key)
                
    ##########################
    # Step 3: Update project #
    ##########################

    st.header("Step 2: Submit your updated project entry")
    is_confirmed = render_confirmation_form(
        data=updated_project,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        driver.projects.update(
            **key,
            project_id=selected_project_id, 
            **updated_project
        )
        rerun(f"Project '{selected_project_id}' has been updated.")



########################################################
# Project UI Option - Remove existing collaboration(s) #
########################################################

def remove_projects(driver: Driver = None, key: Dict[str, str] = {}):
    """ Main function that governs the deletion of metadata in a project 
        within a specified Synergos network
    """
    st.title("Orchestrator - Remove existing collaboration(s)")

    ################################################################
    # Step 1: Pull project information from specified orchestrator #
    ################################################################

    st.header("Step 1: Target your project of interest")
    selected_project_id, retrieved_project = render_projects(
        driver=driver,
        **key 
    )
                
    ################################
    # Step 3: Remove collaboration #
    ################################

    st.header("Step 3: Submit removal request for project")
    is_confirmed = render_confirmation_form(
        data=retrieved_project,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=True    
    )
    if is_confirmed:
        driver.projects.delete(**key, project_id=selected_project_id)
        rerun(f"Project '{selected_project_id}' has been deleted.")


################################
# Project UI - Page Formatting #
################################

def app():
    """ Main app orchestrating project management procedures """
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
        create_projects(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[1]:
        browse_projects(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[2]:
        update_projects(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[3]:
        remove_projects(driver, combination_key)