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
import time
import uuid
from typing import Dict, Any, Union

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
from synui.renderer import (
    CollaborationRenderer, 
    ProjectRenderer,
    ExperimentRenderer,
    RunRenderer,
    ParticipantRenderer,
    RegistrationRenderer,
    TagRenderer,
    AlignmentRenderer
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

#################
# State Helpers #
#################

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


#####################
# Rendering Helpers #
#####################

def render_svg(
    svg_path: str, 
    column: st.delta_generator.DeltaGenerator = None
):
    """ Renders the given svg image given its path
    
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

        st.header("GRID")

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

    if orchestrator_host and orchestrator_port:
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
    SUPPORTED_RECORDS = ["collaboration", "project", "experiment", "run"]
   
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

    return combination_key

    
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
    with st.beta_expander("Confirmation Form"):

        left_column, right_column = st.beta_columns(2)

        with left_column:
            is_previewed = st.checkbox(
                label=f"Preview {r_type} entry",
                value=False,
                key="confirmation"
            )

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

        with right_column:
            if is_previewed:
                with st.echo(code_location="below"):
                    st.write(data)

    return is_correct and is_submitted


def render_collaborations(driver: Driver = None, show_details: bool = True):
    """ Renders out retrieved collaboration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        show_details (bool): Toogles if collaboration details should be shown 
    Returns:
        Selected collaboration ID    (str)
        Updated collaboration record (dict)
    """
    if driver:
        collab_data = driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in collab_data]
    else:
        collab_ids = []

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="""Select a collaboration to peruse."""
        )

        if not show_details:
            return selected_collab_id, None
            
        if driver:
            selected_collab_data = driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
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
    if driver and collab_id:
        project_data = driver.projects.read_all(collab_id).get('data', [])
        project_ids = [proj['key']['project_id'] for proj in project_data]
    else:
        project_ids = []

    with st.beta_container():

        selected_project_id = st.selectbox(
            label="Project ID:", 
            options=project_ids,
            help="""Select a project to peruse."""
        )

        if not show_details:
            return selected_project_id, None

        if driver:
            selected_project_data = driver.projects.read(
                collab_id=collab_id,
                project_id=selected_project_id
            ).get('data', {})
        else:
            selected_project_data = {}

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
    if driver and collab_id and project_id:
        expt_data = driver.experiments.read_all(
            collab_id=collab_id, 
            project_id=project_id
        ).get('data', [])
        expt_ids = [expt['key']['expt_id'] for expt in expt_data]
    else:
        expt_ids = []
    
    with st.beta_container():

        selected_expt_id = st.selectbox(
            label="Experiment ID:", 
            options=expt_ids,
            help="""Select an experiment to peruse."""
        )

        if not show_details:
            return selected_expt_id, None

        if driver:
            selected_expt_data = driver.experiments.read(
                collab_id=collab_id,
                project_id=project_id,
                expt_id=selected_expt_id
            ).get('data', {})
        else:
            selected_expt_data = {}
            
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
    if driver and collab_id and project_id and expt_id:
        run_data = driver.runs.read_all(
            collab_id=collab_id, 
            project_id=project_id,
            expt_id=expt_id
        ).get('data', [])
        run_ids = [run['key']['run_id'] for run in run_data]
    else:
        run_ids = []
    
    with st.beta_container():

        selected_run_id = st.selectbox(
            label="Run ID:", 
            options=run_ids,
            help="""Select an run to peruse."""
        )

        if not show_details:
            return selected_run_id, None

        if driver:
            selected_run_data = driver.runs.read(
                collab_id=collab_id,
                project_id=project_id,
                expt_id=expt_id,
                run_id=selected_run_id
            ).get('data', {})
        else:
            selected_run_data = {}

        if selected_run_data:
            selected_run_data.pop('relations')  # no relations rendering
        
        with st.beta_expander("Run Details"):
            updated_run = (
                run_renderer.display(selected_run_data)
                if form_type == "display"
                else run_renderer.modify(selected_run_data)
            )

    return selected_run_id, updated_run


def render_participant(driver: Driver = None):
    """
    """
    selected_participant_id = st.text_input(
        label="Participant ID:",
        help="""Declare your username."""
    )

    if driver and selected_participant_id:
        participant_data = driver.participants.read(
            participant_id=selected_participant_id
        ).get('data', {})
    else:
        participant_data = {}

    with st.beta_expander("Participant Details"):
        updated_profile = participant_renderer.display(participant_data)
        
    return selected_participant_id, updated_profile


def render_registrations(
    driver: Driver = None, 
    participant_id: str = "",
    collab_id: str = "", 
    project_id: str = ""
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
    
    # Type 2 view: Participant's Perspective
    elif driver and participant_id:
        participant_details = driver.participants.read(
            participant_id=participant_id
        ).get('data', {})
        registry_data = participant_details.get('relations', {}).get('Registration', [])
        participant_ids = [participant_id]

    # Type 3 view: Insufficiant keys -> Render nothing
    else:
        registry_data = []
        participant_ids = []

    with st.beta_container():

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

        with st.beta_expander("Participant Details"):
            participant_details = selected_registry.get('participant', {})
            updated_particicpant = participant_renderer.display(participant_details)

        with st.beta_container():
            left_column, mid_column, right_column = st.beta_columns(3)

            with left_column:
                with st.beta_expander("Registration Details"):
                    updated_registration = reg_renderer.display(selected_registry)

            with mid_column:
                with st.beta_expander("Tag Details"):
                    tags = selected_registry.get('relations', {}).get('Tag', [])
                    tag_details = tags.pop() if tags else {}
                    updated_tags = tag_renderer.display(tag_details)

            with right_column:
                with st.beta_expander("Alignment Details"):
                    alignments = selected_registry.get('relations', {}).get('Alignment', [])
                    alignment_details = alignments.pop() if alignments else {}
                    align_renderer.display(alignment_details)

    return (
        selected_participant_id, 
        updated_particicpant,
        updated_registration,
        updated_tags
    )



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

"""Frameworks for running multiple Streamlit applications as a single app.
"""

class MultiApp:
    """Framework for combining multiple streamlit applications.
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
        self.apps = {}

    def add_app(self, title, func):
        """Adds a new application.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        """
        self.apps[title] = func

    def run(self):
        selected_title = st.sidebar.selectbox(
            'What do you want to do?',
            list(self.apps.keys())
        )
        app = self.apps[selected_title]
        app()


if __name__ == '__main__':
    st.markdown("""
                ## How to download files in Streamlit with download_button()
                ~> Below are use cases and code examples for the `download_button()`
                function, which returns a clickable download link given your data
                file as input.
                See the `Show code example` at the bottom of each section for a
                code snippet you can copy & paste.
                [Recommend improvements here](https://discuss.streamlit.io/)
                The download_button() function is an extension of a workaround based on
                the discussions covered in more detail at [Awesome Streamlit](http://awesome-streamlit.org/).
                Go to Gallery -> Select the App Dropdown -> Choose "File Download Workaround"
                for more information.""")

    st.markdown('-'*17)


    # ---------------------
    # Download from memory
    # ---------------------
    if st.checkbox('Download object from memory'):
        st.write('~> Use if you want to save some data from memory (e.g. pd.DataFrame, dict, list, str, int)')

        # Enter text for testing
        s = st.selectbox('Select dtype', ['list',  # TODO: Add more
                                          'str',
                                          'int',
                                          'float',
                                          'dict',
                                          'bool',
                                          'pd.DataFrame'])
        
        filename = st.text_input('Enter output filename and ext (e.g. my-dataframe.csv, my-file.json, my-list.txt)', 'my-file.json')

        # Pickle Rick
        pickle_it = st.checkbox('Save as pickle file')

        sample_df = pd.DataFrame({'x': list(range(10)), 'y': list(range(10))})
        sample_dtypes = {'list': [1,'a', [2, 'c'], {'b': 2}],
                         'str': 'Hello Streamlit!',
                         'int': 17,
                         'float': 17.0,
                         'dict': {1: 'a', 'x': [2, 'c'], 2: {'b': 2}},
                         'bool': True,
                         'pd.DataFrame': sample_df}

        # Display sample data
        st.write(f'#### Sample `{s}` to be saved to `{filename}`')
        st.code(sample_dtypes[s], language='python')

        # Download sample
        download_button_str = download_button(sample_dtypes[s], filename, f'Click here to download {filename}', pickle_it=pickle_it)
        st.markdown(download_button_str, unsafe_allow_html=True)

        if st.checkbox('Show code example '):
            code_text = f"""
                        s = {sample_dtypes[s]}
                        download_button_str = download_button(s, '{filename}', 'Click here to download {filename}', pickle_it={pickle_it})
                        st.markdown(download_button_str, unsafe_allow_html=True)"""

            st.code(code_text, language='python')

    # --------------------------
    # Select a file to download
    # --------------------------
    if st.checkbox('Select a file to download'):
        st.write('~> Use if you want to test uploading / downloading a certain file.')

        # Upload file for testing
        folder_path = st.text_input('Enter directory: deafult .', '.')
        filename = file_selector(folder_path=folder_path)

        # Load selected file
        with open(filename, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, filename, f'Click here to download {filename}')
        st.markdown(download_button_str, unsafe_allow_html=True)

        if st.checkbox('Show code example'):
            code_text = f"""
                        with open('{filename}', 'rb') as f:
                            s = f.read()
                        download_button_str = download_button(s, '{filename}', 'Click here to download {filename}')
                        st.markdown(download_button_str, unsafe_allow_html=True)"""

            st.code(code_text, language='python')