#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
import uuid

# Libs
import streamlit as st

# Custom
from synergos import Driver
from synui.renderer import ParticipantRenderer
from synui.utils import (
    rerun,
    render_id_generator,
    render_orchestrator_inputs,
    render_confirmation_form,
    render_participant,
    render_collaborations,
    render_projects,
    render_registrations
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create a New Profile",
    "View Profile",
    "Update Profile",
    "Remove Profile"
]

R_TYPE = "participant"

participant_renderer = ParticipantRenderer()

###########
# Helpers #
###########


############################################
# Participant UI Option - Create a profile #
############################################

def create_profile(driver: Driver = None):
    """ Main function that governs the creation of participant profiles within
        a specified Synergos network
    """
    st.title(f"Participant - {SUPPORTED_ACTIONS[0]}")

    ########################
    # Step 0: Introduction #
    ########################


    ########################################
    # Step 1: Declare participant metadata #
    ########################################

    st.header("Step 1: Customize your Profile")
    participant_id = render_id_generator(r_type=R_TYPE)

    with st.beta_container():
        columns = st.beta_columns(2)

        with columns[0]:
            description = participant_renderer.render_profile_summary()
            contacts = participant_renderer.render_contact_details()

        with columns[1]:
            categories = {
                'category': json.loads(
                    st.text_area(label="Categories:", value=[])
                )
            }
            socials = participant_renderer.render_profile_socials()

    ##################################
    # Step 3: Register particicipant #
    ##################################

    st.header("Step 2: Submit your profile entry")
    participant_configurations = {
        **description,
        **categories,
        **contacts,
        **socials
    }
    is_confirmed = render_confirmation_form(
        data=participant_configurations,
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:
        driver.participants.create(
            participant_id=participant_id,
            **participant_configurations
        )
        rerun(f"Participant '{participant_id}' has been created.")



###############################################
# Collaboration UI Option - View your profile #
###############################################

def view_profile(driver: Driver = None):
    """ Main function that governs the browsing of collaborations within a
        specified Synergos network
    """
    st.title(f"Participant - {SUPPORTED_ACTIONS[1]}")

    ########################
    # Step 0: Introduction #
    ########################


    ################################################################
    # Step 1: Pull profile information from specified orchestrator #
    ################################################################

    st.header("Step 1: View your Profile Information")
    participant_id, updated_profile = render_participant(driver=driver)

    ########################################################################
    # Step 2: Pull associations & relationships of specified collaboration #
    ########################################################################

    # st.header("Step 3: Explore Relationships & Associations")
    # selected_project_id, _ = render_projects(
    #     driver=collab_driver, 
    #     collab_id=selected_collab_id
    # )

    # selected_expt_id, _ = render_experiments(
    #     driver=collab_driver, 
    #     collab_id=selected_collab_id,
    #     project_id=selected_project_id
    # )
    
    # render_runs(
    #     driver=collab_driver, 
    #     collab_id=selected_collab_id,
    #     project_id=selected_project_id,
    #     expt_id=selected_expt_id
    # )

    # ###########################################################
    # # Step 4: Browse registrations of specified collaboration #
    # ###########################################################

    # st.header("Step 4: Browse Participant Registry")
    # render_registrations(
    #     driver=collab_driver,
    #     collab_id=selected_collab_id,
    #     project_id=selected_project_id
    # )



##############################################################
# Collaboration UI Option - Update existing collaboration(s) #
##############################################################

def update_profile(driver: Driver = None):
    """ Main function that governs the updating of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title("Orchestrator - Update existing collaboration(s)")

    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    st.header("Step 1: Connect to an Orchestrator")
    collab_driver = render_orchestrator_inputs()

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 2: Modify your collaboration of interest")
    if collab_driver:
        collab_data = collab_driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in collab_data]
    else:
        collab_ids = []

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="""Select a collaboration to peruse."""
        )

        if collab_driver:
            selected_collab_data = collab_driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
            updated_collab = collab_renderer.display(selected_collab_data)
                
    ##################################
    # Step 3: Register collaboration #
    ##################################

    st.header("Step 3: Submit your collaboration entry")
    is_confirmed = render_confirmation_form(
        data=updated_collab,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        collab_driver.collaborations.update(
            collab_id=selected_collab_id, 
            **updated_collab
        )



##############################################################
# Collaboration UI Option - Remove existing collaboration(s) #
##############################################################

def delete_profile(driver: Driver = None):
    """ Main function that governs the deletion of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title("Orchestrator - Remove existing collaboration(s)")

    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    st.header("Step 1: Connect to an Orchestrator")
    collab_driver = render_orchestrator_inputs()

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 2: Target your collaboration of interest")
    if collab_driver:
        collab_data = collab_driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in collab_data]
    else:
        collab_ids = []

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="""Select a collaboration to peruse."""
        )

        if collab_driver:
            selected_collab_data = collab_driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
            updated_collab = collab_renderer.display(selected_collab_data)
                
    ################################
    # Step 3: Remove collaboration #
    ################################

    st.header("Step 3: Submit removal request for collaboration ")
    is_confirmed = render_confirmation_form(
        data=updated_collab,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=False    
    )
    if is_confirmed:
        collab_driver.collaborations.delete(collab_id=selected_collab_id)
        st.echo(f"Collaboration '{selected_collab_id}' has been deleted.")
            


######################################
# Collaboration UI - Page Formatting #
######################################

def app():
    """ Main app orchestrating collaboration management procedures """
    option = st.sidebar.selectbox(
        label='Select action to perform:', 
        options=SUPPORTED_ACTIONS,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    driver = render_orchestrator_inputs()

    if option == SUPPORTED_ACTIONS[0]:
        create_profile(driver)

    elif option == SUPPORTED_ACTIONS[1]:
        view_profile(driver)

    elif option == SUPPORTED_ACTIONS[2]:
        update_profile(driver)

    elif option == SUPPORTED_ACTIONS[3]:
        delete_profile(driver)