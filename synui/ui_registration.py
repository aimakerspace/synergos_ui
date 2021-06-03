#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import streamlit as st

# Custom
from synergos import Driver
from synui.renderer import ParticipantRenderer
from synui.utils import (
    render_orchestrator_inputs,
    render_confirmation_form,
    render_collaborations,
    render_projects,
    render_experiments,
    render_runs,
    render_registrations
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create a new profile",
    "View profile",
    "Update profile",
    "Remove profile"
]

R_TYPE = "participant"

paticipant_renderer = ParticipantRenderer()

###########
# Helpers #
###########


#########################################################
# Collaboration UI Option - Create new Collaboration(s) #
#########################################################

def create_collaborations():
    """ Main function that governs the creation of collaborations within a
        specified Synergos network
    """
    st.title("Orchestrator - Create New Collaboration(s)")

    ########################
    # Step 0: Introduction #
    ########################

    basic_input_container = st.beta_container()
    left_column, mid_column, right_column = basic_input_container.beta_columns(3)

    collab_id = left_column.text_input(
        label="Collaboration ID:",
        help="Declare the name of your new collaboration."
    )

    synergos_variant = mid_column.selectbox(
        label="Variant:",
        options=list(DEFAULT_DEPLOYMENTS.keys()),
        help="Declare which variant of Synergos you deployed for this collaboration."
    )

    deployment_mode = right_column.selectbox(
        label="Mode:",
        options=["local", "distributed"],
        help="""Declare which setting was Synergos deployed in. Selecting 
        'local' indicates that all components have been deployed onto the same 
        server. Conversely, selecting 'distributed' indicates a more complex
        network deployed."""
    )

    default_host = "localhost" if deployment_mode == 'local' else ""

    ##############################################################
    # Step 1: Connect Synergos Driver to a deployed orchestrator #
    ############################################################## 

    st.header("Step 1: Connect to your Orchestrator")
    driver_input_container = st.beta_container()
    left_column, right_column = driver_input_container.beta_columns(2)

    orchestrator_options = ["TTP" if synergos_variant != "SynCluster" else "Director"]
    orchestrator_deployed = left_column.selectbox(
        label="Orchestrator Type", 
        options=orchestrator_options,
        help="Orchestrator type will be dynamically inferred given your specified variant."
    )
    orchestrator_host = right_column.text_input(
        label="Orchestrator IP:",
        value=default_host,
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = right_column.number_input(
        label="Orchestrator Port:",
        value=5000,
        help="Declare the access port of your selected orchestrator."
    )
    driver = Driver(host=orchestrator_host, port=orchestrator_port)

    ###########################################
    # Step 2: Declare all deployed components #
    ########################################### 

    st.header("Step 2: Declare all components of your Synergos Network")

    optional_components_deployed = st.multiselect(
        label="Supplementary components deployed for collaboration:", 
        options=[
            "Synergos Catalogue",
            "Synergos Logger",
            "Synergos Meter",
            "Synergos MLOps",
            "Synergos MQ",
            "Synergos UI"
        ], 
        default=DEFAULT_DEPLOYMENTS[synergos_variant],
        help="Declare which Addons were deployed alongside the core components."
    )

    collab_task = driver.collaborations
    for idx, component in enumerate(optional_components_deployed, start=1):

        st.markdown(f"{idx}. Register specs for {component}:")
        
        if component == "Synergos Catalogue":
            catalogue_info = collab_renderer.render_catalogue_metadata()
            collab_task.configure_catalogue(
                host=catalogue_info['catalogue_host'], 
                port=catalogue_info['catalogue_port']
            )

        elif component == "Synergos Logger":
            logger_info = collab_renderer.render_logger_metadata()
            logger_ports = logger_info['logger_ports']
            collab_task.configure_logger(
                host=logger_info['logger_host'], 
                sysmetrics_port=logger_ports['sysmetrics'],
                director_port=logger_ports['director'],
                ttp_port=logger_ports['ttp'],
                worker_port=logger_ports['worker']
            )

        elif component == "Synergos Meter":
            meter_info = collab_renderer.render_meter_metadata()
            collab_task.configure_meter(
                host=meter_info['meter_host'], 
                port=meter_info['meter_port']
            )

        elif component == "Synergos MLOps":
            mlops_info = collab_renderer.render_mlops_metadata()
            collab_task.configure_mlops(
                host=mlops_info['mlops_host'], 
                port=mlops_info['mlops_port']
            )

        elif component == "Synergos MQ":
            mq_info = collab_renderer.render_mq_metadata()
            collab_task.configure_mq(
                host=mq_info['mq_host'], 
                port=mq_info['mq_port']
            )

        elif component == "Synergos UI":
            ui_info = collab_renderer.render_ui_metadata()
            collab_task.configure_ui(
                host=ui_info['ui_host'], 
                port=ui_info['ui_port']
            )

    ##################################
    # Step 3: Register collaboration #
    ##################################

    st.header("Step 3: Submit your collaboration entry")
    collaboration_configurations = collab_task._compile_configurations()
    is_confirmed = render_confirmation_form(
        data=collaboration_configurations,
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:
        collab_task.create(collab_id=collab_id)



##############################################################
# Collaboration UI Option - Browse Existing Collaboration(s) #
##############################################################

def browse_collaborations():
    """ Main function that governs the browsing of collaborations within a
        specified Synergos network
    """
    st.title("Orchestrator - Browse Existing Collaboration(s)")

    ########################
    # Step 0: Introduction #
    ########################


    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    st.header("Step 1: Connect to an Orchestrator")
    collab_driver = render_orchestrator_inputs()

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 2: Select your collaboration of interest")
    selected_collab_id, _ = render_collaborations(driver=collab_driver)

    ########################################################################
    # Step 3: Pull associations & relationships of specified collaboration #
    ########################################################################

    st.header("Step 3: Explore Relationships & Associations")
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

    ###########################################################
    # Step 4: Browse registrations of specified collaboration #
    ###########################################################

    st.header("Step 4: Browse Participant Registry")
    render_registrations(
        driver=collab_driver,
        collab_id=selected_collab_id,
        project_id=selected_project_id
    )



##############################################################
# Collaboration UI Option - Update existing collaboration(s) #
##############################################################

def update_collaborations():
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

def remove_collaborations():
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

    if option == "Create new collaboration(s)":
        create_collaborations()

    elif option == "Browse existing collaboration(s)":
        browse_collaborations()

    elif option == "Update existing collaboration(s)":
        update_collaborations()

    elif option == "Remove existing collaboration(s)":
        remove_collaborations()