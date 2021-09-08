#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
import os
from collections import Counter
from io import StringIO
from typing import Dict, List, Any, Tuple

# Libs
import streamlit as st

# Custom
from config import STYLES_DIR
from synergos import Driver
from views.renderer import OptimRenderer
from views.core.processes import TrackedProcess
from views.ui_submission import(
    load_command_station,
    collate_general_statistics,
    collate_model_statistics,
    collate_participant_statistics,
    show_hierarchy,
    perform_healthcheck
)
from views.utils import (
    is_connection_valid,
    wait_for_completion,
    download_button,
    load_custom_css,
    render_orchestrator_inputs,
    render_upstream_hierarchy,
    MultiApp
)

##################
# Configurations #
##################

SUPPORTED_DASHBOARDS = ['Hyperdrive', 'Command Station']

optim_renderer = OptimRenderer()

#########################################
# Submission UI Option - Open Launchpad #
#########################################

def load_hyperdrive(driver: Driver, filters: Dict[str, str]):
    """ Loads up launch page for initializing an optimization job. This 
        corresponds to Phase 2C.
        Note: 
        Only execute this after running at least 1 model! Alignment has to
        occur at least once before!        

    Args:
        driver (Driver): Helper object to facilitate connection
        filters (dict): Composite key set identifying a specific federated job
    """

    st.title("Orchestrator - Federated Hyperparameter Optimization")

    ############################################################
    # Step 1: Summarize metadata about specified federated job #
    ############################################################

    st.header("Summary")

    with st.beta_expander(label="Grid statistics", expanded=True):
        columns = st.beta_columns(2)

        with columns[0]:
            collate_general_statistics(driver, filters)
        with columns[1]:
            collate_participant_statistics(driver, filters)

        collate_model_statistics(driver, filters)

    st.header(f"Hyperdrive")

    columns = st.beta_columns((3, 2))

    with columns[0]:
        show_hierarchy({**filters, 'run_id': "*"})
        has_inactive_components, has_active_grids = perform_healthcheck(driver, filters)
        tuning_parameters = optim_renderer.render_tuning_parameters()
        search_space = optim_renderer.render_upload_mods()

    if has_inactive_components or not has_active_grids:

        with columns[-1]:
            with st.beta_expander(label="Alerts", expanded=True):
                if has_inactive_components:
                    st.error(
                        """
                        One or more of your deployed components cannot be reached! 
                        
                        This could be due to:

                        1. Faulty or misconfigured VMs
                        2. Wrong connection metadata declared

                        Please check and ensure that you have correctly deployed your components.
                        """
                    )
                if not has_active_grids:
                    st.error(
                        """
                        No active grids has been detected!

                        This could be due to:

                        1. Participants having faulty or misconfigured deployments
                        2. Participants registering wrong node connection information

                        Please check and ensure that your participants have correctly deployed their worker nodes.
                        """
                    )
    
    elif not has_inactive_components and has_active_grids:

        if search_space:

            with columns[0]:

                placeholder = st.empty()

                with placeholder.beta_container():
                    is_auto_aligned = st.checkbox(
                        label="Perform state auto-alignment",
                        value=True,
                        key=f"auto_alignment"
                    )
                    is_logged = st.checkbox(
                        label="Display logs",
                        value=False,
                        key=f"log_msg"
                    )
                    is_verbose = False
                    if is_logged:
                        is_verbose = st.checkbox(
                            label="Use verbose view",
                            value=is_verbose,
                            key=f"verbose"
                        )

                    is_submitted = st.button(label="Start", key=f"start_job")

                if is_submitted:
                    placeholder.empty()

                    with st.spinner('Hyperjob in progress...'):
                        driver.optimizations.create(
                            **filters,
                            **search_space,
                            **tuning_parameters,
                            auto_align=is_auto_aligned,
                            log_msgs=is_logged,
                            verbose=is_verbose        
                        )

                    st.info("Hyperjob submitted! You may track your progress via the Command Station.")


#######################################
# Job Submission UI - Page Formatting #
#######################################

def app(action: str):
    """ Main app orchestrating federated job triggers """    

    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_DASHBOARDS[0], func=load_hyperdrive)
    core_app.add_view(title=SUPPORTED_DASHBOARDS[1], func=load_command_station)

    driver = render_orchestrator_inputs()

    if driver:
        filters = render_upstream_hierarchy(r_type="run", driver=driver)
        has_filters = any([id for id in list(filters.values())])
 
        if has_filters:
            core_app.run(action)(driver, filters)

        else:
            st.warning(
                """
                Please specify your hierarchy filters to continue.
                
                You will see this message if:

                    1. You have not create any collaborations
                    2. One or more of the IDs you have declared are invalid
                """
            )

    else:
        st.warning(
            """
            Please declare a valid grid connection to continue.
            
            You will see this message if:

                1. You have not declared your grid in the sidebar
                2. Connection parameters you have declared are invalid
            """
        )