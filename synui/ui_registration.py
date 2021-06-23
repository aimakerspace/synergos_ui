#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import streamlit as st

# Custom
from synergos import Driver
from synui.renderer import RegistrationRenderer, TagRenderer
from synui.utils import (
    rerun,
    render_upstream_hierarchy,
    render_orchestrator_inputs,
    render_confirmation_form,
    render_collaborations,
    render_projects,
    render_participant,
    render_participant_registrations
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
        user_role = registration_renderer.render_role_declaration().get('role')
        node_details = registration_renderer.render_registration_metadata().get('nodes')

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
        data={
            'role': user_role, 
            'nodes': node_details,
            'tags': tag_details
        },
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

            st.write(registration_task.list_nodes())

            registration_task.create(
                collab_id=selected_collab_id,
                project_id=selected_project_id,
                participant_id=participant_id,
                role=user_role
            )
        except:
            st.error("Invalid node metadata declared! Please check and try again!")

        try:
            # Submit tags
            driver.tags.create(
                collab_id=selected_collab_id,
                project_id=selected_project_id,
                participant_id=participant_id,
                **tag_details
            )
        except:
            st.error("Invalid tag hierarchy detected! Please check and try again!")

        rerun(f"Node registrations has been successfully submitted.")



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
            updated_user_role = updated_node_details.get('role')
            updated_node_info = updated_node_details.get('nodes') 
            
            # Submit registrations
            registration_task = driver.registrations
            registration_task.update(
                **key,
                role=updated_user_role,
                **updated_node_info
            )
        except:
            st.error("Invalid node metadata declared! Please check and try again!")

        try:
            # Submit tags
            driver.tags.update(**key, **updated_tags)
        except:
            st.error("Invalid tag hierarchy detected! Please check and try again!")

        rerun(f"Node registrations has been successfully submitted.")



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
            registration_task.delete(**key)
        except:
            st.error("Invalid node metadata declared! Please check and try again!")

        try:
            # Submit tags
            driver.tags.delete(**key)
        except:
            st.error("Invalid tag hierarchy detected! Please check and try again!")

        rerun(f"Node registrations has been successfully submitted.") 


######################################
# Registration UI - Page Formatting #
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

    with st.sidebar.beta_container():
        st.header("USER")

        with st.beta_expander("User Parameters", expanded=True):
            participant_id, _ = render_participant(driver=driver, show_details=False)

    if option == SUPPORTED_ACTIONS[0]:
        create_registrations(driver, participant_id)

    elif option == SUPPORTED_ACTIONS[1]:
        browse_registrations(driver, participant_id)

    elif option == SUPPORTED_ACTIONS[2]:
        update_registrations(driver, participant_id)

    elif option == SUPPORTED_ACTIONS[3]:
        remove_registrations(driver, participant_id)