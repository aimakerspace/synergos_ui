#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from typing import Dict, List

# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.core.processes import TrackedProcess
from views.renderer import ParticipantRenderer, TagRenderer
from views.utils import (
    download_button,
    rerun,
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
    filters: List[Dict[str, str]] = []
):
    """ Loads up inference page for participants wanting to submit a prediction
        request. This corresponds to Phase 3B.
    """
    st.title("Participant - Submit an Inference Job")

    ################################
    # A. Extract hierarchical keys #
    ################################

    columns = st.beta_columns((2,1))

    with columns[0]:
        collab_ids = [keyset.get('collab_id', "") for keyset in filters]
        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="Select a collaboration to peruse."
        )

        project_ids = [
            keyset.get('project_id', "") 
            for keyset in filters
            if keyset.get('collab_id') == selected_collab_id
        ]
        selected_project_id = st.selectbox(
            label="Project ID:", 
            options=project_ids,
            help="""Select a project to peruse."""
        )

        expt_data = driver.experiments.read_all(
            collab_id=selected_collab_id, 
            project_id=selected_project_id
        ).get('data', [])
        expt_ids = [
            expt_record.get('key', {}).get('expt_id', "")
            for expt_record in expt_data
        ]
        selected_expt_id = st.selectbox(
            label="Experiment ID:", 
            options=expt_ids,
            help="""Select an experiment to peruse."""
        )

        run_data = driver.runs.read_all(
            collab_id=selected_collab_id,
            project_id=selected_project_id,
            expt_id=selected_expt_id
        ).get('data', [])
        run_ids = [
            run_record.get('key', {}).get('run_id', "")
            for run_record in run_data
        ]
        selected_run_id = st.selectbox(
            label="Run ID:", 
            options=run_ids,
            help="""Select an run to peruse."""
        )

    tag_details = driver.tags.read(
        participant_id=participant_id,
        collab_id=selected_collab_id,
        project_id=selected_project_id
    ).get('data', {})
    updated_tags = tag_renderer.render_tag_metadata(data=tag_details)

    predict_tags = updated_tags.get('predict', {})

    # Check if model corresponding to job key exists 
    # (i.e. training has completed)
    trained_model = driver.models.read(
        collab_id=selected_collab_id,
        project_id=selected_project_id,
        expt_id=selected_expt_id, 
        run_id=selected_run_id
    ).get('data', {})

    code_columns = st.beta_columns(2)

    with code_columns[0]:
        status = st.text_input(
            label="Status:", 
            key=f"status", 
            value=(
                "completed" 
                if (
                    trained_model and 
                    (predict_tags != tag_details.get('predict', {})) and
                    tag_details.get('predict', {})
                )
                else "idle"
            )
        )

    job_key = {
        'collab_id': selected_collab_id,
        'project_id': selected_project_id,
        'expt_id': selected_expt_id,
        'run_id': selected_run_id,
    }

    if status == "idle":

        with code_columns[0]:
            is_auto_aligned = st.checkbox(
                label="Perform state auto-alignment",
                value=True,
                key=f"auto_align"
            )

            is_submitted = st.button(label="Start", key=f"start")
            if is_submitted:

                with st.spinner('Job in progress...'):

                    driver.predictions.create(
                        tags={selected_project_id: predict_tags},
                        participant_id=participant_id,
                        collab_id=selected_collab_id,
                        project_id=selected_project_id,
                        expt_id=selected_expt_id,
                        run_id=selected_run_id,
                        auto_align=is_auto_aligned
                    )

                st.info("Job Completed! Please refresh to view results.")

    else:
        inferences = driver.predictions.read(
            participant_id=participant_id,
            **job_key
        )

        action = code_columns[0].radio(
            label="Select an action:",
            options=SUPPORTED_OPTIONS,
            key=f"action"
        )
        
        if action == SUPPORTED_OPTIONS[0]:

            with code_columns[-1]:
                with st.echo(code_location="below"):
                    st.write(inferences)

        else:
            with code_columns[0]:
                filename = st.text_input(
                    label="Filename:",
                    value=f"INFERENCE_{job_key['collab_id']}_{job_key['project_id']}_{job_key['expt_id']}_{job_key['run_id']}",
                    help="Specify a custom filename if desired"
                )
                download_name = f"{filename}.json"
                download_tag = download_button(
                    object_to_download={
                        'models': trained_model,
                        'inferences': inferences 
                    },
                    download_filename=download_name,
                    button_text="Download"
                )
                st.markdown(download_tag, unsafe_allow_html=True)



##################################
# Inference UI - Page Formatting #
##################################

def app(action: str):
    """ Main app orchestrating participant inference procedures """

    core_app = MultiApp()
    core_app.add_view(title=SUPPORTED_ACTIONS[0], func=commence_inference)

    driver = render_orchestrator_inputs()

    if driver:

        participant_id, participant_filters = render_cascading_filter(driver)
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