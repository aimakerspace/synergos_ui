#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import streamlit as st

# Custom
from config import SUPPORTED_COMPONENTS, DEFAULT_DEPLOYMENTS
from synergos import Driver
from views.renderer import CollaborationRenderer
from views.utils import (
    download_button,
    is_request_successful,
    render_id_generator,
    render_orchestrator_inputs,
    render_confirmation_form,
    render_collaborations,
    render_projects,
    render_experiments,
    render_runs,
    render_orchestrator_registrations,
    MultiApp,
)

##################
# Configurations #
##################

SUPPORTED_COMPONENT_NAMES = [
    metadata['name'] 
    for metadata in SUPPORTED_COMPONENTS.values()
]

SUPPORTED_ACTIONS = [
    "Create new collaboration(s)",
    "Browse existing collaboration(s)",
    "Update existing collaboration(s)",
    "Remove existing collaboration(s)"
]

R_TYPE = "collaboration"

collab_renderer = CollaborationRenderer()

###########
# Helpers #
###########

# def download_ttp_script():

#     script = "docker run \
#             -p 5000:5000 \
#             -v /home/aisg/Desktop/synergos_demos/ttp_data/:/ttp/data \
#             -v /home/aisg/Desktop/synergos_demos/ttp_outputs/:/ttp/outputs \
#             -v /home/aisg/Desktop/synergos_demos/mlflow_test/:/ttp/mlflow \
#             --rm \
#             --name ttp_syncluster_1 \
#             synergos_ttp:basic \
#                 --id ttp_syncluster_1 \
#                 --logging_variant graylog 172.20.0.4 9300 \
#                 --debug \
#                 --censored"

#     with left_column:
#         is_downloaded = st.checkbox(label="Export architecture")
    
#     with right_column:
#         if is_downloaded:
#             filename = st.text_input(
#                 label="Filename:",
#                 value=f"ARCH_{collab_id}_{project_id}_{expt_id}",
#                 help="Specify a custom filename if desired"
#             )
#             is_pickled = st.checkbox('Save as pickle file')
#             download_name = (
#                 f"{filename}.pkl" 
#                 if is_pickled 
#                 else f"{filename}.json"
#             )
#             download_tag = download_button(
#                 object_to_download=model,
#                 download_filename=download_name,
#                 button_text="Download"
#             )
#             st.markdown(download_tag, unsafe_allow_html=True)


#########################################################
# Collaboration UI Option - Create new Collaboration(s) #
#########################################################

def create_collaborations(driver: Driver = None):
    """ Main function that governs the creation of collaborations within a
        specified Synergos network
    """       
    st.title(f"Orchestrator - {SUPPORTED_ACTIONS[0]}")

    ########################
    # Step 0: Introduction #
    ########################


    ##############################################
    # Step 1: Declare orchestrator configuration #
    ##############################################

    st.header("Step 1: Declare your collaboration configuration")

    collab_id = render_id_generator(r_type=R_TYPE)

    columns = st.beta_columns(3)

    synergos_variant = columns[0].selectbox(
        label="Configuration:",
        options=list(DEFAULT_DEPLOYMENTS.keys()),
        help="Declare which variant of Synergos you deployed for this collaboration."
    )

    deployment_mode = columns[1].selectbox(
        label="Mode:",
        options=["local", "distributed"],
        help="""Declare which setting was Synergos deployed in. Selecting 
        'local' indicates that all components have been deployed onto the 
        same server. Conversely, selecting 'distributed' indicates a more 
        complex network deployed."""
    )
    default_host = "localhost" if deployment_mode == 'local' else ""

    orchestrator_options = ["Director" if synergos_variant == "Synergos Cluster" else "TTP"]
    orchestrator_deployed = columns[2].selectbox(
        label="Orchestrator Type", 
        options=orchestrator_options,
        help="Orchestrator type will be dynamically inferred given your specified variant."
    )

    ###########################################
    # Step 2: Declare all deployed components #
    ########################################### 

    st.header("Step 2: Declare additional components for your collaboration")

    optional_components_deployed = st.multiselect(
        label="Supplementary components deployed for collaboration:", 
        options=SUPPORTED_COMPONENT_NAMES, 
        default=DEFAULT_DEPLOYMENTS[synergos_variant],
        help="Declare which Addons were deployed alongside the core components."
    )

    collab_task = driver.collaborations
    for idx, component_name in enumerate(optional_components_deployed, start=1):
        
        with st.beta_expander(
            label=f"{idx}. Register specs for {component_name}",
            expanded=False
        ):
            if component_name == "Synergos Catalogue":
                catalogue_info = collab_renderer.render_catalogue_metadata()
                if catalogue_info:
                    collab_task.configure_catalogue(**catalogue_info)

            elif component_name == "Synergos Logger":
                logger_info = collab_renderer.render_logger_metadata()
                if logger_info:
                    collab_task.configure_logger(**logger_info)

            elif component_name == "Synergos Meter":
                meter_info = collab_renderer.render_meter_metadata()
                if meter_info:
                    collab_task.configure_meter(**meter_info)

            elif component_name == "Synergos MLOps":
                mlops_info = collab_renderer.render_mlops_metadata()
                if mlops_info:
                    collab_task.configure_mlops(**mlops_info)

            elif component_name == "Synergos MQ":
                mq_info = collab_renderer.render_mq_metadata()
                if mq_info:
                    collab_task.configure_mq(**mq_info)

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
        create_resp = collab_task.create(collab_id=collab_id)
        is_request_successful(create_resp)


##############################################################
# Collaboration UI Option - Browse Existing Collaboration(s) #
##############################################################

def browse_collaborations(driver: Driver = None):
    """ Main function that governs the browsing of collaborations within a
        specified Synergos network
    """
    st.title(f"Orchestrator - {SUPPORTED_ACTIONS[1]}")

    ########################
    # Step 0: Introduction #
    ########################


    ######################################################################
    # Step 1: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 1: Select your collaboration of interest")
    selected_collab_id, _ = render_collaborations(driver=driver)

    ########################################################################
    # Step 2: Pull associations & relationships of specified collaboration #
    ########################################################################

    st.header("Step 2: Explore Relationships & Associations")
    selected_project_id, _ = render_projects(
        driver=driver, 
        collab_id=selected_collab_id
    )

    selected_expt_id, _ = render_experiments(
        driver=driver, 
        collab_id=selected_collab_id,
        project_id=selected_project_id
    )
    
    render_runs(
        driver=driver, 
        collab_id=selected_collab_id,
        project_id=selected_project_id,
        expt_id=selected_expt_id
    )

    ###########################################################
    # Step 3: Browse registrations of specified collaboration #
    ###########################################################

    st.header("Step 3: Browse Participant Registry")
    render_orchestrator_registrations(
        driver=driver,
        collab_id=selected_collab_id,
        project_id=selected_project_id
    )



##############################################################
# Collaboration UI Option - Update existing collaboration(s) #
##############################################################

def update_collaborations(driver: Driver = None):
    """ Main function that governs the updating of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title(f"Orchestrator - {SUPPORTED_ACTIONS[2]}")

    ######################################################################
    # Step 1: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 1: Modify your collaboration of interest")
    selected_collab_id, updated_collab = render_collaborations(driver=driver)
                
    collab_task = driver.collaborations
    removed_components = {}
    for component, updated_info in updated_collab.items():
        
        if updated_info:
            if component == "catalogue":
                collab_task.configure_catalogue(**updated_info)

            elif component == "logs":
                collab_task.configure_logger(**updated_info)

            elif component == "meter":
                collab_task.configure_meter(**updated_info)

            elif component == "mlops":
                collab_task.configure_mlops(**updated_info)

            elif component == "mq":
                collab_task.configure_mq(**updated_info)
        else:
            removed_components[component] = updated_info

    ##################################
    # Step 2: Register collaboration #
    ##################################

    st.header("Step 2: Submit your collaboration entry")
    updated_configurations = {
        **collab_task._compile_configurations(), 
        **removed_components
    }
    is_confirmed = render_confirmation_form(
        data=updated_configurations,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:

        update_resp = collab_task.update(
            collab_id=selected_collab_id,
            **removed_components  # for component deletion, manually override
        )

        is_request_successful(update_resp)


##############################################################
# Collaboration UI Option - Remove existing collaboration(s) #
##############################################################

def remove_collaborations(driver: Driver = None):
    """ Main function that governs the deletion of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title(f"Orchestrator - {SUPPORTED_ACTIONS[3]}")

    ######################################################################
    # Step 1: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 1: Target your collaboration of interest")
    selected_collab_id, updated_collab = render_collaborations(driver=driver)
                
    ################################
    # Step 2: Remove collaboration #
    ################################

    st.header("Step 2: Submit removal request for collaboration ")
    is_confirmed = render_confirmation_form(
        data=updated_collab,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=True    
    )
    if is_confirmed:
        delete_resp = driver.collaborations.delete(collab_id=selected_collab_id)
        is_request_successful(delete_resp)



######################################
# Collaboration UI - Page Formatting #
######################################

def app(action: str):
    """ Main app orchestrating collaboration management procedures """
    
    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=create_collaborations)
    core_app.add_view(title=SUPPORTED_ACTIONS[1], func=browse_collaborations)
    core_app.add_view(title=SUPPORTED_ACTIONS[2], func=update_collaborations)
    core_app.add_view(title=SUPPORTED_ACTIONS[3], func=remove_collaborations)

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
            """
        )
