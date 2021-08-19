#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json

# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.renderer import ParticipantRenderer
from views.utils import (
    is_request_successful,
    render_id_generator,
    render_orchestrator_inputs,
    render_confirmation_form,
    render_participant,
    render_participant_registrations,
    MultiApp
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
        create_resp = driver.participants.create(
            participant_id=participant_id,
            **participant_configurations
        )
        is_request_successful(create_resp)



###############################################
# Collaboration UI Option - View your profile #
###############################################

def view_profile(driver: Driver = None):
    """ Main function that governs the browsing of collaborations within a
        specified Synergos network
    """
    st.title(f"{R_TYPE.capitalize()} - {SUPPORTED_ACTIONS[1]}")

    ########################
    # Step 0: Introduction #
    ########################


    ################################################################
    # Step 1: Pull profile information from specified orchestrator #
    ################################################################

    st.header("Step 1: View your Profile Information")
    participant_id, _ = render_participant(driver=driver)

    ########################################################################
    # Step 2: Pull associations & relationships of specified collaboration #
    ########################################################################

    st.header("Step 2: Explore Relationships & Associations")
    render_participant_registrations(
        driver=driver, 
        participant_id=participant_id
    )

    # Things to render:
    # 1) collaborations participant is part of
        # 1a) project that participant under collab is part of
        # 1b) Registered nodes
        # 1c) Submitted dataset tags



##############################################################
# Collaboration UI Option - Update existing collaboration(s) #
##############################################################

def update_profile(driver: Driver = None):
    """ Main function that governs the updating of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title(f"{R_TYPE.capitalize()} - {SUPPORTED_ACTIONS[2]}")

    ######################################################################
    # Step 1: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header(f"Step 1: Modify your profile")
    participant_id, updated_profile = render_participant(driver=driver)

    ##################################
    # Step 2: Register collaboration #
    ##################################

    st.header(f"Step 2: Submit your changes")
    is_confirmed = render_confirmation_form(
        data=updated_profile,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        update_resp = driver.participants.update(
            participant_id=participant_id, 
            **updated_profile
        )
        is_request_successful(update_resp)



##############################################################
# Collaboration UI Option - Remove existing collaboration(s) #
##############################################################

def delete_profile(driver: Driver = None):
    """ Main function that governs the deletion of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title(f"{R_TYPE.capitalize()} - {SUPPORTED_ACTIONS[3]}")

    ######################################################################
    # Step 1: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header(f"Step 1: Specify your profile ID")
    participant_id, updated_profile = render_participant(driver=driver)

    ################################
    # Step 2: Remove collaboration #
    ################################

    st.header(f"Step 2: Submit a removal request")
    is_confirmed = render_confirmation_form(
        data=updated_profile,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=True    
    )
    if is_confirmed:
        delete_resp = driver.participants.delete(participant_id=participant_id)
        is_request_successful(delete_resp)
            


######################################
# Collaboration UI - Page Formatting #
######################################

def app(action: str):
    """ Main app orchestrating participant profile management procedures """
    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=create_profile)
    core_app.add_view(title=SUPPORTED_ACTIONS[1], func=view_profile)
    core_app.add_view(title=SUPPORTED_ACTIONS[2], func=update_profile)
    core_app.add_view(title=SUPPORTED_ACTIONS[3], func=delete_profile)

    driver = render_orchestrator_inputs()

    if driver:
        core_app.run(action)(driver)

    else:
        st.warning(
            """
            Please declare a valid grid connection to continue.
            
            You will see this message if:

                1. You have not declared your grid in the sidebar
                2. Connection parameters you have declared are invalid

            Please verify your connection metadata with your assisting
            ochestrator, before trying again.
            """
        )