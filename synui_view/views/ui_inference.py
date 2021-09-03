#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
from typing import Dict, List
from numpy.lib.function_base import place

# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.core.processes import TrackedInference
from views.renderer import ParticipantRenderer, TagRenderer
from views.ui_submission import collate_model_statistics
from views.utils import (
    download_button,
    render_orchestrator_inputs,
    render_cascading_filter,
    render_participant,
    render_participant_registrations,
    MultiApp
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = ["Submit inference request"]
SUPPORTED_OPTIONS = ["Preview results", "Download results"]

participant_renderer = ParticipantRenderer()
tag_renderer = TagRenderer()

###########
# Helpers #
###########


#####################################################
# Inference UI Option - Submit an inference request #
#####################################################

def commence_inference(
    driver: Driver = None, 
    participant_id: str = "",
    filters: Dict[str, str] = {}
):
    """ Loads up inference page for participants wanting to submit a prediction
        request. This corresponds to Phase 3B.

    Args:
        driver (Driver): Helper object to facilitate connection
        participant_id (str): ID of participant
        filters (dict): Composite key set identifying a specific federated job
    """
    st.title("Participant - Submit an Inference Job")

    #######################################################
    # 0A. Show model statistics to assist model selection #
    #######################################################

    st.header("Summary")
    with st.beta_expander(label="Statistics", expanded=True):
        collate_model_statistics(driver, filters)

    ###################################################
    # 0B. Show participants their reference data tags #
    ###################################################

    st.header("Datasets")
    with st.beta_expander(label="1. View your reference tags", expanded=False):
        tag_details = driver.tags.read(
            participant_id=participant_id,
            **filters
        ).get('data', {})
        tag_renderer.render_tag_metadata(
            data=tag_details,
            tags=["train", "evaluate"]
        )

    ####################################################
    # 1. Participants to declare their prediction tags #
    ####################################################

    with st.beta_expander(label="2. Declare your prediction tags", expanded=False):
        predict_tags = tag_renderer.render_tag_metadata(
            data=tag_details,
            tags=["predict"]
        ).get('predict', {})


    st.header("Configurations")
    code_columns = st.beta_columns((3, 2))

    ################################
    # 2. Extract hierarchical keys #
    ################################

    expt_data = driver.experiments.read_all(**filters).get('data', [])
    expt_ids = [
        expt_record.get('key', {}).get('expt_id', "")
        for expt_record in expt_data
    ]
    selected_expt_id = code_columns[0].selectbox(
        label="Experiment ID:", 
        options=expt_ids,
        help="""Select an experiment to peruse."""
    )

    run_data = driver.runs.read_all(
        **filters,
        expt_id=selected_expt_id
    ).get('data', [])
    run_ids = [
        run_record.get('key', {}).get('run_id', "")
        for run_record in run_data
    ]
    selected_run_id = code_columns[0].selectbox(
        label="Run ID:", 
        options=run_ids,
        help="""Select an run to peruse."""
    )

    #############################
    # 3. Check inference status #
    #############################

    job_key = {
        **filters,
        'expt_id': selected_expt_id,
        'run_id': selected_run_id,
    }


    fl_job = TrackedInference(
        driver=driver, 
        participant_id=participant_id, 
        filters=job_key
    ) 
    detected_status = fl_job.check()
    idle_key = fl_job.statuses[0]
    in_progress_key = fl_job.statuses[1]
    completed_key = fl_job.statuses[2]

    manual_status = code_columns[0].text_input(
        label="Status:", 
        key="status", 
        value=detected_status,
        help="""
            Detected status of the tracked inference job. 
            
            You can override this by specifying 'Idle' to restart the process.
            """
    )

    # Edge 1: Orchestrator is forcing a rerun of a completed job
    if detected_status == completed_key and manual_status == idle_key:

        with code_columns[1]:
            with st.beta_expander(label="Alerts", expanded=True):
                st.warning(
                    """
                    You have chosen to override the current job state.

                    This will rerun the current federated job.

                    Your previous results will be erased.

                    Please confirm to proceed.
                    """
                )

        with code_columns[0]:
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

        inferences = driver.predictions.read(
            participant_id=participant_id,
            **job_key
        )

        with code_columns[0]:
            action = st.radio(
                label="Select an action:",
                options=SUPPORTED_OPTIONS,
                key=f"action"
            )
        
            if action == SUPPORTED_OPTIONS[0]:

                with st.beta_expander(label="Preview", expanded=False):
                    st.code(
                        json.dumps(inferences, sort_keys=True, indent=4),
                        language="json"
                    )

            else:

                filename = st.text_input(
                    label="Filename:",
                    value=f"INFERENCE_{job_key['collab_id']}_{job_key['project_id']}_{job_key['expt_id']}_{job_key['run_id']}",
                    help="Specify a custom filename if desired"
                )
                download_name = f"{filename}.json"
                download_tag = download_button(
                    object_to_download={
                        'inferences': inferences 
                    },
                    download_filename=download_name,
                    button_text="Download"
                )
                st.markdown(download_tag, unsafe_allow_html=True)

    #########################################################################
    # Step 3b: If federated job is still in progress, alert and do nothing  #
    #########################################################################

    elif detected_status == in_progress_key:

        with code_columns[1]:
            fl_job.track_access()
            start_time = fl_job.retrieve_start_time()
            access_counts = fl_job.retrieve_access_counts()

            with st.beta_expander(label="Alerts", expanded=True):
                st.warning(
                    f"""
                    Requested job is still in progress. 
                    
                    Start time              : {start_time}

                    No. of times visited    : {access_counts} 
                    """
                )

    elif detected_status == idle_key:

        with code_columns[0]:

            placeholder = st.empty()

            with placeholder.beta_container():
                is_auto_aligned = st.checkbox(
                    label="Perform state auto-alignment",
                    value=True,
                    key=f"auto_align"
                )

                is_submitted = st.button(label="Start", key="start")

            if is_submitted:
                placeholder.empty()
                
                fl_job.start()
                with st.spinner('Job in progress...'):

                    driver.predictions.create(
                        tags={job_key['project_id']: predict_tags},
                        participant_id=participant_id,
                        **job_key,
                        auto_align=is_auto_aligned
                    )

                fl_job.stop()
                st.info("Job Completed! Please refresh to view results.")


##################################
# Inference UI - Page Formatting #
##################################

def app(action: str):
    """ Main app orchestrating participant inference procedures """

    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=commence_inference)

    driver = render_orchestrator_inputs()

    if driver:

        participant_id, participant_filters = render_cascading_filter(
            driver,
            r_type="experiment"
        )
        if participant_id:
            core_app.run(action)(driver, participant_id, participant_filters)

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