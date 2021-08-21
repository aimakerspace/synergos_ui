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

#########################################
# Submission UI Option - Open Launchpad #
#########################################

def load_hyperparameter_ranges():
    """
    """
    with st.beta_container():

        uploaded_file = st.file_uploader(
            label="Upload your hyperparameter ranges:",
            type="json",
            help="Provide a parsable JSON file documenting each layer of your desired model"    
        )

        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            stringio = StringIO(bytes_data.decode("utf-8"))
            hyperparam_string = stringio.read()
            hyperparam_ranges = {"search_space": json.loads(hyperparam_string)}
        else:
            hyperparam_ranges = {}

    return hyperparam_ranges  


def load_hyperdrive(driver: Driver, filters: Dict[str, str]):
    """
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

        hyperparameter_ranges = load_hyperparameter_ranges()

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

        fl_job = TrackedProcess(
            driver=driver, 
            p_type="optimization", 
            filters=filters
        ) 
        detected_status = fl_job.check()

        with columns[0]:
            manual_status = st.text_input(
                label="Status:", 
                key="process_status", 
                value=detected_status
            )

        idle_key = fl_job.statuses[0]
        in_progress_key = fl_job.statuses[1]
        completed_key = fl_job.statuses[2]

        # Edge 1: Orchestrator is forcing a rerun of a completed job
        if detected_status == completed_key and manual_status == idle_key:

            with columns[1]:
                with st.beta_expander(label="Alerts", expanded=True):
                    st.warning(
                        """
                        You have chosen to override current hyperjob state.

                        This will rerun the current hyperjob set. Due to the
                        nature of generation, you may get different results.

                        Please confirm to proceed.
                        """
                    )
            with columns[0]:
                is_forced = st.selectbox(
                    label="Are you sure you want to force a rerun?",
                    options=["No", "Yes"],
                    key=f"forced_rerun"
                ) == "Yes"
                
            detected_status = manual_status if is_forced else detected_status
        
        ########################################################################
        # Step 3a: If federated job has already completed, preview & download  #
        ########################################################################

        if detected_status == completed_key:

            # Show top X performing models
            pass

        #########################################################################
        # Step 3b: If federated job is still in progress, alert and do nothing  #
        #########################################################################

        elif detected_status == in_progress_key:

            with columns[1]:
                fl_job.track_access()
                start_time = fl_job.retrieve_start_time()
                access_counts = fl_job.retrieve_access_counts()

                with st.beta_expander(label="Alerts", expanded=True):
                    st.warning(
                        f"""
                        Requested Hyperjob is still in progress. 
                        
                        Start time              : {start_time}

                        No. of times visited    : {access_counts} 
                        """
                    )

        ####################################################################
        # Step 3c: If federated job has not been trained before, start it  #
        ####################################################################

        elif detected_status == idle_key:

            with columns[0]:
                is_auto_aligned = st.checkbox(
                    label="Perform state auto-alignment",
                    value=True,
                    key=f"auto_alignment"
                )
                is_auto_fixed = st.checkbox(
                    label="Perform architecture auto-fixing",
                    value=True,
                    key=f"auto_fix"
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

                    fl_job.start()
                    with st.spinner('Hyperjob in progress...'):

                        driver.alignments.create(
                            **filters,
                            auto_align=is_auto_aligned,
                            auto_fix=is_auto_fixed
                        ).get('data', [])

                        driver.models.create(
                            **filters,
                            auto_align=is_auto_aligned,
                            dockerised= True,
                            log_msgs=is_logged,
                            verbose=is_verbose
                        ).get('data', [])

                        driver.validations.create(
                            **filters,
                            auto_align=is_auto_aligned,
                            dockerised= True,
                            log_msgs=is_logged,
                            verbose=is_verbose
                        ).get('data', [])

                    fl_job.stop()
                    st.info("Hyperjob Completed! Please refresh to view results.")




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