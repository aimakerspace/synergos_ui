#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from typing import Dict

# Libs
import streamlit as st

# Custom
from synergos import Driver
from views.renderer import ParticipantRenderer, TagRenderer
from views.utils import (
    download_button,
    rerun,
    render_orchestrator_inputs,
    render_cascading_filter,
    render_participant,
    render_participant_registrations
)

##################
# Configurations #
##################

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
    participant_id: str = None,
    filters: Dict[str, str] = {}
):
    """
    """
    st.title("Participant - Submit an Inference Job")

    # Extract individual keys
    filtered_collab_id = filters.get('collab_id', None)
    filtered_project_id = filters.get('project_id', None)
    filtered_expt_id = filters.get('expt_id', None)
    filtered_run_id = filters.get('run_id', None)  

    # A. Filter out relevant collaborations
    if driver and not filtered_collab_id:
        all_collabs = driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in all_collabs]

    elif driver and filtered_collab_id:
        collab_ids = [filtered_collab_id]

    else:
        collab_ids = []

    federated_jobs = []
    for collab_id in collab_ids:

        # B. Filter out relevant projects
        if driver and not filtered_project_id:
            all_projects = driver.projects.read_all(
                collab_id=collab_id
                ).get('data', [])
            project_ids = [project['key']['project_id'] for project in all_projects]
        
        elif driver and filtered_project_id:
            project_ids = [filtered_project_id]

        else:
            project_ids = []

        for project_id in project_ids:

            # C. Filter out relevant experiments
            if driver and not filtered_expt_id:
                all_expts = driver.experiments.read_all(
                    collab_id=collab_id, 
                    project_id=project_id
                    ).get('data', [])
                expt_ids = [expt['key']['expt_id'] for expt in all_expts]
            
            elif driver and filtered_expt_id:
                expt_ids = [filtered_expt_id]

            else:
                expt_ids = []

            for expt_id in expt_ids:

                # D. Filter out relevant runs
                if driver and not filtered_run_id:
                    all_runs = driver.runs.read_all(
                        collab_id=collab_id, 
                        project_id=project_id, 
                        expt_id=expt_id
                        ).get('data', [])
                    job_keys = [run['key'] for run in all_runs]
                
                elif driver and filtered_run_id:
                    run = driver.runs.read(
                        collab_id=collab_id, 
                        project_id=project_id, 
                        expt_id=expt_id, 
                        run_id=filtered_run_id
                        ).get('data', {})
                    job_keys = [run['key']]

                else:
                    job_keys = []

                federated_jobs += job_keys

    # List out all collaborations in hierarchy
    for _idx, job_key in enumerate(federated_jobs):
        
        with st.beta_container():
            st.markdown("---")

            columns = st.beta_columns((1, 2))
            
            with columns[0]:
                st.text_input(
                    label="Collaboration ID:", 
                    value=job_key.get('collab_id', ""),
                    key=f"collab_{_idx}"
                )
                st.text_input(
                    label="Project ID:", 
                    value=job_key.get('project_id', ""),
                    key=f"project_{_idx}"
                )
                st.text_input(
                    label="Experiment ID:", 
                    value=job_key.get('expt_id', ""),
                    key=f"experiment_{_idx}"
                )
                st.text_input(
                    label="Run ID:", 
                    value=job_key.get('run_id', ""),
                    key=f"run_{_idx}"
                )

            if driver and participant_id:
                tag_details = driver.tags.read(
                    participant_id=participant_id,
                    collab_id=job_key.get('collab_id'),
                    project_id=job_key.get('project_id')
                ).get('data', {})
            else:
                tag_details = {}

            updated_tags = tag_renderer.render_tag_metadata(
                data=tag_details,
                signature=_idx
            )
            predict_tags = updated_tags.get('predict', {})

            # Check if model corresponding to job key exists 
            # (i.e. training has completed)
            trained_model = driver.models.read(**job_key).get('data', {})

            code_columns = st.beta_columns(2)

            with code_columns[0]:
                status = st.text_input(
                    label="Status:", 
                    key=f"status_{_idx}", 
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


            if status == "idle":

                with code_columns[0]:
                    is_auto_aligned = st.checkbox(
                        label="Perform state auto-alignment",
                        value=True,
                        key=f"auto_align_{_idx}"
                    )

                    is_submitted = st.button(label="Start", key=f"start_{_idx}")
                    if is_submitted:

                        with st.spinner('Job in progress...'):

                            driver.predictions.create(
                                tags={job_key.get('project_id'): predict_tags},
                                participant_id=participant_id,
                                **job_key,
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
                    key=f"action_{_idx}"
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

def app():
    """ Main app orchestrating collaboration management procedures """

    driver = render_orchestrator_inputs()

    with st.sidebar.beta_container():
        st.header("USER")

        with st.beta_expander("User Parameters", expanded=True):
            participant_id, _ = render_participant(driver=driver, show_details=False)

    # key_filters = render_cascading_filter()

    commence_inference(
        driver=driver, 
        participant_id=participant_id,
        filters={}#key_filters    
    )