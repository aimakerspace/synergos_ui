#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import streamlit as st

# Custom
from synergos import Driver
from synui.utils import (
    render_collaborations,
    render_projects,
    render_experiments,
    render_runs
)

##################
# Configurations #
##################

SUPPORTED_ENTITIES = ["Project", "Experiment", "Run"]

SUPPORTED_ACTIONS = [
    "Create new entries",
    "Browse existing entries",
    "Update existing entries",
    "Remove existing entries"
]
    # if synergos_variant == "cluster":
    #     st.number_input(
    #         label="No. of grids deployed",
    #         min_value=1, 
    #         max_value=None, 
    #         step=1,
    #         help="Declare no. of grids deployed")

###########
# Helpers #
###########


##############################################
# Submission UI Option - Create new entry(s) #
##############################################

def create_job_entry():
    st.title("Orchestrator - Submit a Federated Job")

    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    # st.header("Step 1: Connect to an Orchestrator")

    basic_input_container = st.beta_container()
    left_column, right_column = basic_input_container.beta_columns(2)

    orchestrator_host = left_column.text_input(
        label="Orchestrator IP:",
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = right_column.number_input(
        label="Orchestrator Port:",
        value=5000,
        help="Declare the access port of your selected orchestrator."
    )
    if orchestrator_host and orchestrator_port:
        collab_driver = Driver(host=orchestrator_host, port=orchestrator_port)
    else:
        collab_driver = None    # Ensures rendering of unpopulated widgets

    with st.beta_container():
        columns = st.beta_columns(4)

        with columns[0]:
            selected_collab_id, _ = render_collaborations(
                collab_driver,
                show_details=False
            )

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    selected_project_id, _ = render_projects(
        driver=collab_driver, 
        collab_id=selected_collab_id
    )

    selected_expt_id, _ = render_experiments(
        driver=collab_driver, 
        collab_id=selected_collab_id,
        project_id=selected_project_id
    )
    
    render_runs(
        driver=collab_driver, 
        collab_id=selected_collab_id,
        project_id=selected_project_id,
        expt_id=selected_expt_id
    )



#######################################
# Job Submission UI - Page Formatting #
#######################################

def app():
    """ Main app orchestrating collaboration management procedures """
    entity_option = st.sidebar.radio(
        label='Select entity to manage:', 
        options=SUPPORTED_ENTITIES,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    action_option = st.sidebar.selectbox(
        label='Select action to perform:', 
        options=SUPPORTED_ACTIONS,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    if action_option == "Create new entries":
        create_job_entry()

    elif action_option == "Browse existing entries":
        pass

    elif action_option == "Update existing entries":
        pass

    elif action_option == "Remove existing entries":
        pass