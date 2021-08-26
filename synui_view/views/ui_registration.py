#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.renderer import RegistrationRenderer, TagRenderer
from views.utils import (
    is_request_successful,
    render_orchestrator_inputs,
    render_cascading_filter,
    render_confirmation_form,
    render_collaborations,
    render_projects,
    render_participant_registrations,
    MultiApp
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create a new registration",
    "View registration(s)",
    "Update registration(s)",
    "Remove registration(s)"
]

USER_TYPE = "Participant"
R_TYPE = "registration"

registration_renderer = RegistrationRenderer()
tag_renderer = TagRenderer() 

###########
# Helpers #
###########


#######################################################
# Registration UI Option - Create new Registration(s) #
#######################################################

def create_registrations(driver: Driver = None, participant_id: str = None):
    """ Main function that governs the creation of collaborations within a
        specified Synergos network
    """
    st.title(f"{USER_TYPE} - {SUPPORTED_ACTIONS[0]}")

    ########################
    # Step 0: Introduction #
    ########################


    ###################################################################
    # Step 1:  Select which collaboration and project to register for #
    ###################################################################

    st.header("Step 1: Select your project")
    selected_collab_id, _ = render_collaborations(driver, show_details=False)
    selected_project_id, _ = render_projects(
        driver=driver,
        collab_id=selected_collab_id
    )

    ###########################################
    # Step 2: Register your compute resources #
    ###########################################

    st.header("Step 2: Register your compute resources")
    with st.beta_expander("Node Registration"):
        user_role = registration_renderer.render_role_declaration()
        node_details = registration_renderer.render_registration_metadata()

    ######################################
    # Step 3: Register your dataset tags #
    ######################################

    st.header("Step 3: Register your dataset tags")
    with st.beta_expander("Tag Registration"):
        tag_details = tag_renderer.render_tag_metadata()

    ##########################################
    # Step 4: Submit your registration entry #
    ##########################################

    st.header(f"Step 4: Submit your {R_TYPE} entry")
    is_confirmed = render_confirmation_form(
        data={**user_role, 'nodes': node_details, 'tags': tag_details},
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:

        try:
            # Submit registrations
            registration_task = driver.registrations
            for _, info in sorted(node_details.items(), key=lambda x: x[0]):
                registration_task.add_node(**info)

            reg_create_resp = registration_task.create(
                collab_id=selected_collab_id,
                project_id=selected_project_id,
                participant_id=participant_id,
                **user_role
            )
            st.info("Processing node registrations...")
            is_request_successful(reg_create_resp)
        except:
            st.error("Invalid node metadata declared! Please check and try again!")

        try:
            # Submit tags
            tag_create_resp = driver.tags.create(
                collab_id=selected_collab_id,
                project_id=selected_project_id,
                participant_id=participant_id,
                **tag_details
            )
            st.info("Processing data tag registrations...")
            is_request_successful(tag_create_resp)
        except:
            st.error("Invalid tag hierarchy detected! Please check and try again!")



############################################################
# Registration UI Option - Browse Existing Registration(s) #
############################################################

def browse_registrations(driver: Driver = None, participant_id: str = None):
    """ Main function that governs the browsing of collaborations within a
        specified Synergos network
    """
    st.title(f"{USER_TYPE} - {SUPPORTED_ACTIONS[1]}")

    ########################
    # Step 0: Introduction #
    ########################


    #################################################################
    # Step 1:  Select which collaboration and project to browse for #
    #################################################################

    st.header("Step 1: Browse by Filters")
    render_participant_registrations(
        driver=driver,
        participant_id=participant_id
    )



############################################################
# Registration UI Option - Update existing Registration(s) #
############################################################

def update_registrations(driver: Driver = None, participant_id: str = None):
    """ Main function that governs the updating of registration and tag 
        metadata of a participant within a specified Synergos network
    """
    st.title(f"{USER_TYPE} - {SUPPORTED_ACTIONS[2]}")

    ##################################################################
    # Step 1: Pull participant hierarchy from specified orchestrator #
    ##################################################################

    st.header("Step 1: Modify your registration of interest")
    key, updated_node_details, updated_tags = render_participant_registrations(
        driver=driver,
        participant_id=participant_id
    )

    ############################
    # Step 2: Register changes #
    ############################

    st.header("Step 2: Submit your registration updates")
    is_confirmed = render_confirmation_form(
        data={**updated_node_details, 'tags': updated_tags},
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )

    if is_confirmed:
        
        try:           
            # Submit registrations
            registration_task = driver.registrations
            reg_update_resp = registration_task.update(
                **key, 
                **updated_node_details
            )
            st.info("Processing node registrations...")
            is_request_successful(reg_update_resp)
        except:
            st.error("Invalid node metadata declared! Please check and try again!")

        try:
            # Submit tags
            tag_update_resp = driver.tags.update(**key, **updated_tags)
            st.info("Processing data tag registrations...")
            is_request_successful(tag_update_resp)
        except:
            st.error("Invalid tag hierarchy detected! Please check and try again!")



###################################################################
# Registration UI Option - Remove existing registration(s) & tags #
###################################################################

def remove_registrations(driver: Driver = None, participant_id: str = None):
    """ Main function that governs the deletion of registration and tag 
        metadata of a participant within a specified Synergos network
    """
    st.title(f"{USER_TYPE} - {SUPPORTED_ACTIONS[3]}")

    ######################################################################
    # Step 1: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 1: Target your registration of interest")
    key, updated_node_details, updated_tags = render_participant_registrations(
        driver=driver,
        participant_id=participant_id
    )

    ################################
    # Step 2: Remove collaboration #
    ################################

    st.header("Step 2: Submit your registration updates")
    is_confirmed = render_confirmation_form(
        data={**updated_node_details, 'tags': updated_tags},
        r_type=R_TYPE,
        r_action="update",
        use_warnings=True    
    )
    if is_confirmed:
        
        try:           
            # Submit registrations
            registration_task = driver.registrations
            delete_resp = registration_task.delete(**key)

            # By virtue of hierarchical cascade, all associated tags  will
            # automatically be deleted as well

            st.info("Processing deletion request...")
            is_request_successful(delete_resp)
            
        except:
            st.error("Invalid node metadata declared! Please check and try again!")



######################################
# Registration UI - Page Formatting #
######################################

def app(action: str):
    """ Main app orchestrating collaboration management procedures """
    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=create_registrations)
    core_app.add_view(title=SUPPORTED_ACTIONS[1], func=browse_registrations)
    core_app.add_view(title=SUPPORTED_ACTIONS[2], func=update_registrations)
    core_app.add_view(title=SUPPORTED_ACTIONS[3], func=remove_registrations)

    driver = render_orchestrator_inputs()

    if driver:
        
        participant_id, _ = render_cascading_filter(driver, show_details=False)
        if participant_id:
            core_app.run(action)(driver, participant_id)

        else:
            st.warning("Please state your Participant ID to continue.")

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