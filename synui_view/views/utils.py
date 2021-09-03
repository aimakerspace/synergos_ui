#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import base64
import os
import json
import pickle
import re
import socket
import time
import uuid
from typing import Callable, Dict, List, Any, Union

# Libs
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import streamlit.report_thread as ReportThread
from streamlit.hashing import _CodeHasher
from streamlit.script_request_queue import RerunData
from streamlit.script_runner import RerunException
from streamlit.server.server import Server

# Custom
from synergos import Driver
from views.renderer import (
    CollaborationRenderer, 
    ProjectRenderer,
    ExperimentRenderer,
    RunRenderer,
    ParticipantRenderer,
    RegistrationRenderer,
    TagRenderer,
    AlignmentRenderer,
    OptimRenderer
)

##################
# Configurations #
##################

collab_renderer = CollaborationRenderer()
project_renderer = ProjectRenderer()
expt_renderer = ExperimentRenderer()
run_renderer = RunRenderer()
reg_renderer = RegistrationRenderer()
tag_renderer = TagRenderer()
participant_renderer = ParticipantRenderer()
align_renderer = AlignmentRenderer()
optim_renderer = OptimRenderer()

###################
# General Helpers #
###################

def load_custom_css(css_path: str):
    """ Helper function that loads in and combines all custom static CSS rules 
        declared as a HTML tag string. This is a temporary hack to inject
        custom designs & formats into Streamlit

    Args:
        css_path (str): Path to CSS rules
    """
    with open(css_path, "r") as csp:
        loaded_styles = csp.read()

    styles_string = f"<style>{loaded_styles}</style>"
    st.markdown(styles_string, unsafe_allow_html=True)

#################
# State Helpers #
#################

def is_connection_valid(host: str, port: int) -> bool:
    """ Given a set of host and port mappings, pre-runs connection diagnostics 
        to check if connection information declared is valid (i.e. server is
        reachable)

    Args:
        host (str): IP address of server to test
        port (int): Port allocation of connection to test
    Returns:
        Connection state (bool)
    """
    if not host:
        return False

    try:
        # Check if there is a DNS listening
        detected_host = socket.gethostbyname(host)

        # Check if the host is actually reachable
        s = socket.create_connection((detected_host, port), 2)
        s.close()
        return True

    except:
        return False


def is_request_successful(resp: dict):
    """ Parses a REST response for its status code and renders a corresponding
        onscreen notification

    Args:
        resp (dict): JSON payload received from REST-RPC
    Returns:
        Status (bool) 
    """
    status_code = resp.get('status')
    if status_code >= 200 and status_code < 300: 
        st.success("Request successfully completed.")
        return True
    else:
        st.error(
            """
            Something when wrong during your submission!

            Please check that all declared parameters are correct and try again.
            """
        )
        return False


def rerun(msg: str = None, delay: int = 3):
    """ Rerun a Streamlit app from the top of current loaded script.
        
        Note:
        This is a solution adapted from an issue documented at 
        https://gist.github.com/tvst/ef477845ac86962fa4c92ec6a72bb5bd. The
        idea is to grab the state of widgets on the current page. However, the
        main different between the current implementation and the suggested
        solution is that Steamlit's latest version has officialized extraction
        of widget states differently.

    Args:
        msg (str): Optional message to print out as notification to the user
        delay (int): Time delay between message print-out and page reset
    """
    if msg:
        st.info(msg)
        time.sleep(delay)

    ctx = ReportThread.get_report_ctx()
    widget_states = ctx.widgets

    # st.write(dir(list(widget_states._state.items())[0][1]))

    # TARGET_WIDGETS = ["confirmation"]
    # for w_idx, widget in widget_states._state.items():
    #     for w_type in TARGET_WIDGETS:
    #         if w_type in w_idx:
    #             if getattr(widget, 'bool_value', None) is not None:
    #                 st.write("Before:", widget)
    #                 widget.bool_value = not widget.bool_value
    #                 widget.trigger_value = not widget.trigger_value
    #                 st.write("After:", widget)

    st.caching.clear_cache()
    raise RerunException(RerunData(widget_states))


class _SessionState:

    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)
        
    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value
    
    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()
    
    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False
        
        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = ReportThread.get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    
    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


#####################
# Rendering Helpers #
#####################

def render_svg(
    svg_path: str, 
    column: st.delta_generator.DeltaGenerator = None
):
    """ Renders the given svg image given its path as Base64 byte code
    
    Args:
        svg_path (str): Path to SVG image to be rendered 
    """
    with open(svg_path, "rb") as image:
        svg = image.read()
        b64 = base64.b64encode(svg).decode("utf-8")

    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    if column:
        column.write(html, unsafe_allow_html=True)
    else:
        st.write(html, unsafe_allow_html=True)

    return html


def render_png(
    png_path: str, 
    column: st.delta_generator.DeltaGenerator = None,
    autoload: bool = True,
    *args
):
    """ Renders the given PNG image given its path as Base64 byte code
    
    Args:
        png_path (str): Path to PNG image to be rendered 
    """
    with open(png_path, "rb") as image:
        png = image.read()
        b64 = base64.b64encode(png).decode("utf-8")

    format_param_str = " ".join(args)
    html = r'<img src="data:image/png;base64,%s" %s/>' % (b64, format_param_str)
    
    if autoload:
        if column:
            column.write(html, unsafe_allow_html=True)
        else:
            st.write(html, unsafe_allow_html=True)

    return html


def render_id_generator(r_type: str = ""):
    """ Renders an input form that grants the option of generating a random ID
        in addition to a manual declaration
    
    Args:
        r_type (str): Type of document/archival record handled
    Returns:
        Randomly generated ID (str)
    """
    with st.beta_container():

        id_screen = st.empty()

        id_label = " ".join([r_type.lower().capitalize(), "ID:"])
        help_string = f"Declare the name of your new {r_type}"
        random_id = f"{r_type.upper()}_{uuid.uuid4()}"
        
        is_generated = st.checkbox(label="Auto-generate")
        init_value = random_id if is_generated else ""
        declared_id = id_screen.text_input(
            label=id_label,
            value=init_value,
            help=help_string
        )

    return declared_id


def render_orchestrator_inputs() -> Union[Driver, None]:
    """ Renders input form for collecting orchestrator-related connection
        metadata, and assembles a Synergos Driver object for subsequent use.

    Returns:
        Connected Synergos Driver (Driver)
    """
    with st.sidebar.beta_container():

        st.header("NETWORK")

        with st.beta_expander("Orchestrator Parameters", expanded=True):
        
            orchestrator_host = st.text_input(
                label="Orchestrator IP:",
                help="Declare the server IP of your selected orchestrator."
            )
            orchestrator_port = st.number_input(
                label="Orchestrator Port:",
                value=5000,
                help="Declare the access port of your selected orchestrator."
            )

    if is_connection_valid(host=orchestrator_host, port=orchestrator_port):
        driver = Driver(host=orchestrator_host, port=orchestrator_port)
    else:
        driver = None    # Ensures rendering of unpopulated widgets

    return driver


def render_upstream_hierarchy(r_type: str, driver: Driver) -> Dict[str, str]:
    """ Renders input form for collecting keys corresponding to a record's
        upstream hierarchy for subsequent use.

    Args:
        r_type (str): Type of document/archival record handled
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
    Returns:
        All relevant keys (dict)          
    """
    SUPPORTED_RECORDS = ["collaboration", "project", "experiment", "run", "model"]
   
    with st.sidebar.beta_container():

        st.header("FILTERS")

        with st.beta_expander("Key Parameters", expanded=True):
            
            combination_key = {}

            if r_type in SUPPORTED_RECORDS[1:]:
                selected_collab_id, _ = render_collaborations(
                    driver=driver,
                    show_details=False
                )
                combination_key['collab_id'] = selected_collab_id

                if r_type in SUPPORTED_RECORDS[2:]:
                    selected_project_id, _ = render_projects(
                        driver=driver,
                        collab_id=selected_collab_id,
                        show_details=False
                    )
                    combination_key['project_id'] = selected_project_id

                    if r_type in SUPPORTED_RECORDS[3:]:
                        selected_expt_id, _ = render_experiments(
                            driver=driver,
                            collab_id=selected_collab_id,
                            project_id=selected_project_id,
                            show_details=False
                        )
                        combination_key['expt_id'] = selected_expt_id

                        if r_type in SUPPORTED_RECORDS[4:]:
                            selected_run_id, _ = render_runs(
                                driver=driver,
                                collab_id=selected_collab_id,
                                project_id=selected_project_id,
                                expt_id=selected_expt_id,
                                show_details=False
                            )
                            combination_key['run_id'] = selected_run_id

    return combination_key


def render_cascading_filter(
    driver: Driver,
    r_type: str = "",
    show_details: bool = True
) -> Dict[str, str]:
    """ Renders a dynamic filter that allows users to traverse the federated
        job hierarchy for participants

    Returns:
        Composite Filtering keys (dict)
    """
    SUPPORTED_RECORDS = ["collaboration", "project", "experiment", "run", "model"]

    with st.sidebar.beta_container():
        st.header("USER")

        with st.beta_expander("User Parameters", expanded=True):
            participant_id, _ = render_participant(
                driver=driver, 
                show_details=False
            )

    if not show_details:
        return participant_id, None

    if participant_id:
        participant_data = driver.participants.read(participant_id).get('data', {})   
        participant_relations = participant_data.get('relations', {})
        participant_registrations = participant_relations.get('Registration', [])
        participant_filters = [
            reg_record.get('key', {})
            for reg_record in participant_registrations
        ]
    else:
        participant_filters = []

    with st.sidebar.beta_container():

        st.header("FILTERS")

        with st.beta_expander("Key Parameters", expanded=True):

            combination_key = {}

            if r_type in SUPPORTED_RECORDS[1:]:
                collab_ids = [
                    keyset.get('collab_id', "") 
                    for keyset in participant_filters
                ]
                selected_collab_id = st.selectbox(
                    label="Collaboration ID:", 
                    options=collab_ids,
                    help="Select a collaboration to peruse."
                )
                combination_key['collab_id'] = selected_collab_id

                if r_type in SUPPORTED_RECORDS[2:]:
                    project_ids = [
                        keyset.get('project_id', "") 
                        for keyset in participant_filters
                        if keyset.get('collab_id') == selected_collab_id
                    ]
                    selected_project_id = st.selectbox(
                        label="Project ID:", 
                        options=project_ids,
                        help="""Select a project to peruse."""
                    )
                    combination_key['project_id'] = selected_project_id

                    if r_type in SUPPORTED_RECORDS[3:]:
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
                        combination_key['expt_id'] = selected_expt_id

                        if r_type in SUPPORTED_RECORDS[4:]:
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
                            combination_key['run_id'] = selected_run_id

    return participant_id, combination_key

    
def render_confirmation_form(
    data: Dict[str, Any], 
    r_type: str = "",
    r_action: str = "",
    use_warnings: bool = False
) -> bool:
    """ Renders declaration form for users to verify if the metadata they are
        about to submit is correct

    Args:
        data (dict): Metadata related to a specific process
        r_type (str): Type of document/archival record handled
        r_action (str): Type of action (i.e. CRUD) to execute on archived data
        use_warnings (bool): Toggles if extra warning interaction is active
    Returns:
        Confirmation state (bool)
            True    if participant has confirmed and intends to submit
            False   otherwise 
    """       
    is_correct = False
    is_submitted = False

    with st.beta_expander("Confirmation Form"):

        columns = st.beta_columns((2, 3))

        with columns[0]:

            confirmation_options = [
                f"Preview {r_type} entry", 
                f"Finalize {r_type} submission"
            ]
            selected_option = st.radio(
                label="Select an option:",
                options=confirmation_options,
            )

            if selected_option == confirmation_options[1]:

                placeholder = st.empty()
                
                with placeholder.beta_container():
                    is_correct = st.checkbox(
                        label="Confirm if details declared are correct", 
                        value=False,
                        key="confirmation"
                    )
                    if is_correct and use_warnings:
                        is_finalized = st.selectbox(
                            label="Are you sure? This action is not reversible!", 
                            index=1,
                            options=['Yes', 'No'],
                            key="confirmation"
                        )
                        is_correct = is_correct and (is_finalized == 'Yes') 

                    is_submitted = st.button(label="Submit", key="confirmation")

                if is_correct and is_submitted:
                    placeholder.info("Entry confirmed.")

        with columns[1]:
            if selected_option == confirmation_options[0]:
                st.code(
                    json.dumps(data, sort_keys=True, indent=4),
                    language="json"
                )

    return is_correct and is_submitted


def render_collaborations(driver: Driver, show_details: bool = True):
    """ Renders out retrieved collaboration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        show_details (bool): Toogles if collaboration details should be shown 
    Returns:
        Selected collaboration ID    (str)
        Updated collaboration record (dict)
    """
    collab_data = driver.collaborations.read_all().get('data', [])
    collab_ids = [collab['key']['collab_id'] for collab in collab_data]

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="Select a collaboration to peruse."
        )

        if not show_details:
            return selected_collab_id, None
            
        selected_collab_data = driver.collaborations.read(
            collab_id=selected_collab_id
        ).get('data', {})
       
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
            updated_collab = collab_renderer.display(selected_collab_data)

    return selected_collab_id, updated_collab


def render_projects(
    driver: Driver = None, 
    collab_id: str = "",
    show_details: bool = True
):
    """ Renders out retrieved project metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        show_details (bool): Toogles if project details should be shown 
    Returns:
        Selected project ID    (str)
        Updated project record (dict)
    """
    project_data = driver.projects.read_all(collab_id).get('data', [])
    project_ids = [proj['key']['project_id'] for proj in project_data]

    with st.beta_container():

        selected_project_id = st.selectbox(
            label="Project ID:", 
            options=project_ids,
            help="""Select a project to peruse."""
        )

        if not show_details:
            return selected_project_id, None

        selected_project_data = driver.projects.read(
            collab_id=collab_id,
            project_id=selected_project_id
        ).get('data', {})

        if selected_project_data:
            selected_project_data.pop('relations')  # no relations rendering

        with st.beta_expander("Project Details"):
            updated_project = project_renderer.display(selected_project_data)

    return selected_project_id, updated_project


def render_experiments(
    driver: Driver = None, 
    collab_id: str = "", 
    project_id: str = "",
    form_type: str = "display",
    show_details: bool = True
):
    """ Renders out retrieved experiment metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
        form_type (str): What type of form to render (i.e. 'display' or 'modify' 
            mode). This is due to the way at which experiments are declared.
        show_details (bool): Toogles if experiment details should be shown 
    Returns:
        Selected experiment ID    (str)
        Updated experiment record (dict)
    """
    expt_data = driver.experiments.read_all(
        collab_id=collab_id, 
        project_id=project_id
    ).get('data', [])
    expt_ids = [expt['key']['expt_id'] for expt in expt_data]
    
    with st.beta_container():

        selected_expt_id = st.selectbox(
            label="Experiment ID:", 
            options=expt_ids,
            help="""Select an experiment to peruse."""
        )

        if not show_details:
            return selected_expt_id, None

        selected_expt_data = driver.experiments.read(
            collab_id=collab_id,
            project_id=project_id,
            expt_id=selected_expt_id
        ).get('data', {})
            
        if selected_expt_data:
            selected_expt_data.pop('relations')  # no relations rendering

        with st.beta_expander("Experiment Details"):
            updated_experiment = (
                expt_renderer.display(selected_expt_data)
                if form_type == "display"
                else expt_renderer.modify(selected_expt_data)
            )

    return selected_expt_id, updated_experiment


def render_runs(
    driver: Driver = None, 
    collab_id: str = "", 
    project_id: str = "",
    expt_id: str = "",
    form_type: str = "display",
    show_details: bool = True
):
    """ Renders out retrieved run metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
        expt_id (str): ID of selected experiment to be rendered
        form_type (str): What type of form to render (i.e. 'display' or 'modify' 
            mode). This is due to the way at which runs are declared.
        show_details (bool): Toogles if hyperparameters should be shown 
    Returns:
        Selected run ID    (str)
        Updated run record (dict)
    """
    run_data = driver.runs.read_all(
        collab_id=collab_id, 
        project_id=project_id,
        expt_id=expt_id
    ).get('data', [])
    run_ids = [run['key']['run_id'] for run in run_data]
    
    with st.beta_container():

        selected_run_id = st.selectbox(
            label="Run ID:", 
            options=run_ids,
            help="""Select an run to peruse."""
        )

        if not show_details:
            return selected_run_id, None

        selected_run_data = driver.runs.read(
            collab_id=collab_id,
            project_id=project_id,
            expt_id=expt_id,
            run_id=selected_run_id
        ).get('data', {})

        if selected_run_data:
            selected_run_data.pop('relations')  # no relations rendering
        
        with st.beta_expander("Run Details"):
            updated_run = (
                run_renderer.display(selected_run_data)
                if form_type == "display"
                else run_renderer.modify(selected_run_data)
            )

    return selected_run_id, updated_run


def render_participant(
    driver: Driver = None,
    participant_id: str = None,
    show_details: bool = True 
):
    """ Renders out declaration form for specifying a participant to browse.
        Note that this is from the participant's POV (i.e. the participant is 
        expected to know his/her own username)

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        participant_id (str): ID of selected participant
    Returns:

    """
    selected_participant_id = st.text_input(
        label="Participant ID:",
        help="""Declare your username."""
    ) if not participant_id else participant_id

    if not show_details:
        return selected_participant_id, None

    if selected_participant_id:
        participant_data = driver.participants.read(
            participant_id=selected_participant_id
        ).get('data', {})
    else:
        participant_data = {}

    with st.beta_expander("Participant Details"):
        updated_profile = participant_renderer.display(participant_data)
    
    return selected_participant_id, updated_profile


def render_orchestrator_registrations(
    driver: Driver = None, 
    collab_id: str = None, 
    project_id: str = None
):
    """ Renders out retrieved registration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
    """
    # Type 1 view: Orchestrator's Perspective
    if driver and collab_id and project_id:
        registry_data = driver.registrations.read_all(
            collab_id=collab_id, 
            project_id=project_id
        ).get('data', [])
        participant_ids = [reg['key']['participant_id'] for reg in registry_data]

    # Type 2 view: Insufficiant keys -> Render nothing
    else:
        registry_data = []
        participant_ids = []

    selected_participant_id = st.selectbox(
        label="Participant ID:", 
        options=participant_ids,
        help="""Select an participant to view."""
    )

    if registry_data:
        selected_registry = [
            reg for reg in registry_data 
            if reg['key']['participant_id'] == selected_participant_id
        ].pop()
    else:
        selected_registry = {}

    with st.beta_container():

        render_participant(
            driver=driver, 
            participant_id=selected_participant_id
        )

        with st.beta_expander("Registration Details"):
            reg_renderer.display(selected_registry)

        with st.beta_expander("Tag Details"):
            tags = selected_registry.get('relations', {}).get('Tag', [])
            tag_details = tags.pop() if tags else {}
            tag_renderer.display(tag_details)

        with st.beta_expander("Alignment Details"):
            alignments = selected_registry.get('relations', {}).get('Alignment', [])
            alignment_details = alignments.pop() if alignments else {}
            align_renderer.display(alignment_details)

    return selected_participant_id


def render_participant_registrations(
    driver: Driver = None, 
    participant_id: str = None
):
    """ Renders out retrieved registration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
    """
    if participant_id:
        participant_data = driver.participants.read(participant_id).get('data', {})
    else:
        participant_data = {}

    participant_relations = participant_data.get('relations', {})
    participant_registrations = participant_relations.get('Registration', [])
    
    registry_mapping = {}
    for registration in participant_registrations:
        curr_collab_id = registration.get('key', {}).get('collab_id')
        curr_collab = registry_mapping.get(curr_collab_id, {})      
        curr_project_id = registration.get('key', {}).get('project_id') 
        curr_collab[curr_project_id] = registration   
        registry_mapping[curr_collab_id] = curr_collab     

    registered_collab_ids = list(registry_mapping.keys())
    selected_collab_id = st.selectbox(
        label="Collaboration ID:", 
        options=registered_collab_ids,
        help="""Select a collaboration to view."""
    )

    selected_project_id, _ = render_projects(
        driver=driver,
        collab_id=selected_collab_id
    )
   
    with st.beta_expander("Registration Details"):
        relevant_entry = registry_mapping.get(selected_collab_id, {}).get(selected_project_id, {})
        updated_registrations = reg_renderer.display(data=relevant_entry)

    with st.beta_expander("Tag Details"):
        participant_tags = participant_relations.get('Tag', [])
        retrieved_tags = [
            tags 
            for tags in participant_tags
            if (
                set(tags.get('key', {}).values()) == 
                {participant_id, selected_collab_id, selected_project_id}
            )
        ]
        relevant_tags = retrieved_tags.pop() if retrieved_tags else {}
        
        updated_tags = tag_renderer.display(data=relevant_tags)

    composite_key = {
        'participant_id': participant_id,
        'collab_id': selected_collab_id, 
        'project_id': selected_project_id
    } 
    return composite_key, updated_registrations, updated_tags
    

#####################
# Interface Helpers #
#####################

def download_button(
    object_to_download: object, 
    download_filename: str, 
    button_text: str, 
    pickle_it: bool = False
):
    """ Generates a link to download the given object_to_download.
    
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download, indent=4)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
            }}
        </style>
    """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'
    # dl_link = f'<a download="{download_filename}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


def file_selector(folder_path='.'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)



##############################
# Stitching Class - MultiApp #
##############################

class MultiApp:
    """ Framework for combining multiple streamlit applications.
    
    Usage:
        def foo():
            st.title("Hello Foo")
        def bar():
            st.title("Hello Bar")
        app = MultiApp()
        app.add_app("Foo", foo)
        app.add_app("Bar", bar)
        app.run()
    
    It is also possible keep each application in a separate file.
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """
    def __init__(self):
        self.__action_map = {
            'create': 0,
            'browse': 1,
            'update': 2,
            'delete': 3
        }
        self.apps = {}

    ###########
    # Helpers #
    ###########

    def add_view(self, title: str, func: Callable):
        """ Adds a new application view, mapped to a specific action.

        Args:
            title (str): Keyword trigger
            func (Callable): Python function to render this app.
        """
        self.apps[title] = func

    ##################
    # Main Functions #
    ##################

    def run(self, action: str = "create"):
        selected_title = st.sidebar.selectbox(
            'What do you want to do?',
            list(self.apps.keys()),
            index=self.__action_map[action],
            key="action"
        )
        app = self.apps[selected_title]
        return app
