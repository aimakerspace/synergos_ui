#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import copy
import json
import numbers
import pprint
import uuid
from io import StringIO
from typing import Dict, List, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 
from .utils import download_button

##################
# Configurations #
##################

MODIFICATION_OPTIONS = [
    'Upload a new hyperparameter set', 
    'Modify existing hyperparameters'
]

MAX_COLUMNS = 10

####################################
# Run Renderer Class - RunRenderer #
####################################

class RunRenderer(BaseRenderer):
    """ Main class responsible for rendering run-related forms in a streamlit 
        interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_upload_mods(self) -> Dict[str, List[Dict[str, Any]]]:
        """ Renders interface facilitating major architectural declarations for 
            a specific experiment submitted in a Synergos network

        Args:
            data (dict): Information relevant to a registered experiment
        Returns:
            Agumented hyperparameters (dict)
        """
        with st.beta_container():

            uploaded_file = st.file_uploader(
                label="Upload your hyperparameter set:",
                type="json",
                help="Provide a parsable JSON file documenting all desired hyperparameters"    
            )

            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                stringio = StringIO(bytes_data.decode("utf-8"))
                param_string = stringio.read()
                hyperparameters = json.loads(param_string)
            else:
                hyperparameters = {}  

            st.markdown("---")

        return hyperparameters


    def render_hyperparmeters(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[float, int, str]]:
        """ Renders a form capturing existing hyperparameters to be used for a 
            specified run registered in a deployed Synergos network, given its 
            prerequisite run information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered run
        Returns:
            Updated hyperparameters (dict)
        """
        with st.beta_container():
            columns = st.beta_columns(3)

            column_count = columns[0].selectbox(
                label="Columns:",
                options=[i for i in range(1, MAX_COLUMNS + 1)],
                index=6
            )

            st.markdown("---")

        data = copy.deepcopy(data)
        data.pop('doc_id')
        data.pop('kind')
        data.pop('key')

        with st.beta_container():
            columns = st.beta_columns(column_count)

            updated_hyperparameters = {}
            for (idx, 
                (hyperparam_name, hyperparam_value)
            ) in enumerate(data.items(), start=1):

                selected_col_idx = (idx -1) % column_count
                selected_column =  columns[selected_col_idx]

                with selected_column:

                    with st.beta_container():
                    
                        updated_hyperparam_name = st.text_input(
                            label=f"Hyperparameter {idx} - Name:",
                            value=hyperparam_name
                        )

                        if isinstance(hyperparam_value, numbers.Number):
                            updated_hyperparam_value = st.number_input(
                                label=f"Hyperparameter {idx} - Value:",
                                value=hyperparam_value
                            )

                        elif isinstance(hyperparam_value, str):
                            updated_hyperparam_value = st.text_input(
                                label=f"Hyperparameter {idx} - Value:",
                                value=hyperparam_value
                            )

                        else:
                            updated_hyperparam_value = st.text_area(
                                label=f"Hyperparameter {idx} - Value:",
                                value=pprint.pformat(hyperparam_value),
                                height=200,
                                help="Incentive hierarchy to be applied on the project"
                            )

                        st.markdown("---")

                updated_hyperparameters[updated_hyperparam_name] = updated_hyperparam_value

        return updated_hyperparameters


    def render_export_option(self, data: Dict[str, Any] = {}) -> None:
        """ Renders a form capturing existing hyperparameters to be used for a 
            specified run registered in a deployed Synergos network, given its 
            prerequisite run information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered run
        Returns:
            Updated hyperparameters (dict)
        """
        composite_key = data.get('key', {})
        collab_id = composite_key.get('collab_id', "")
        project_id = composite_key.get('project_id', "")
        expt_id = composite_key.get('expt_id', "")
        run_id = composite_key.get('run_id', "")

        data = copy.deepcopy(data)
        data.pop('doc_id')
        data.pop('kind')
        data.pop('key')

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            with left_column:
                is_previewed = st.checkbox(label="Preview hyperparameters")

            with right_column:
                if is_previewed:
                    with st.echo(code_location='below'):
                        st.write(data)

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            with left_column:
                is_downloaded = st.checkbox(label="Export hyperparmeters")
            
            with right_column:
                if is_downloaded:
                    filename = st.text_input(
                        label="Filename:",
                        value=f"HYPERPARAM_{collab_id}_{project_id}_{expt_id}_{run_id}",
                        help="Specify a custom filename if desired"
                    )
                    is_pickled = st.checkbox(
                        label='Save as pickle file',
                        key=uuid.uuid4()
                    )
                    download_name = (
                        f"{filename}.pkl" 
                        if is_pickled 
                        else f"{filename}.json"
                    )
                    download_tag = download_button(
                        object_to_download=run_id,
                        download_filename=download_name,
                        button_text="Download"
                    )
                    st.markdown(download_tag, unsafe_allow_html=True)

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[float, int, str]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registered run.

        Args:
            data (dict): Information relevant to a registered run
        Returns:
            Updated run info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=False)

        st.header("Hyperparameters")
        updated_hyperparameters = self.render_hyperparmeters(data)
        self.render_export_option({**data, **updated_hyperparameters})

        return updated_hyperparameters


    def modify(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, List[Dict[str, Any]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registered experiment.

        Args:
            data (dict): Information relevant to a registered experiment
        Returns:
            Updated experiment info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=False)

        mod_option = st.radio(
            "Select a modification:",
            options=MODIFICATION_OPTIONS
        )

        if mod_option == MODIFICATION_OPTIONS[1]:
            updated_architecture = self.render_hyperparmeters(data)

        else:
            updated_architecture = self.render_upload_mods()

        return updated_architecture