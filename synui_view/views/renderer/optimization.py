#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import json
from io import StringIO
from typing import Dict, List, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 
from .utils import download_button

##################
# Configurations #
##################

MODIFICATION_OPTIONS = [
    'Upload a new architecure', 
    'Modify existing architecture'
]

###############################################
# Optimization Renderer Class - OptimRenderer #
###############################################

class OptimRenderer(BaseRenderer):
    """ Main class responsible for rendering optimization-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_upload_mods(self) -> Dict[str, List[Dict[str, Any]]]:
        """ Renders interface facilitating search space declarations for 
            hyperparameter tuning submitted in a Synergos network.

        Returns:
            Search space (dict)
        """
        with st.beta_container():

            uploaded_file = st.file_uploader(
                label="Upload your hyperparameter ranges:",
                type="json",
                help="Provide a parsable JSON file documenting your search space"    
            )

            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                stringio = StringIO(bytes_data.decode("utf-8"))
                hyperparam_string = stringio.read()
                hyperparam_ranges = {"search_space": json.loads(hyperparam_string)}
            else:
                hyperparam_ranges = {}

        return hyperparam_ranges

        
    def render_tuning_parameters(
        self,
        data: Dict[str, Any] = {}
    ) -> Dict[str, List[Dict[str, Any]]]:
        """ Renders interface facilitating tuner configurations for 
            hyperparmeter tuning submitted in a Synergos network

        Args:

        Returns:

        """
        with st.beta_container():

            metric = st.selectbox(
                label="Select your metric:",
                options=["accuracy"],
                help="Select a metric to optimize on."
            )

            optimize_mode = st.selectbox(
                label="Direction of optimization:",
                options=["max", "min"],
                help="Specify if you want to maximize or minimize your selected metric."
            )

            trial_concurrency = st.number_input(
                label="No. of concurrent trials:",
                min_value=1,

            )

            max_exec_duration = st.number_input(
                label="Time Budget (in seconds):",
                value=3600,
                help="""State a time budget for each trial. A time budget is a 
                        duration after which a trial is forcefully terminated. 
                     """
            )

            max_trial_num = st.number_input(
                label="Max number of trials:",
                value=10,
                help="State a maximum number of trials to generate."
            )

        return {
            'metric': metric,
            'optimize_mode': optimize_mode,
            'trial_concurrency': trial_concurrency,
            'max_exec_duration': max_exec_duration,
            'max_trial_num': max_trial_num
        }




    # def render_minor_mods(
    #     self,
    #     data: Dict[str, Any] = {}
    # ) -> Dict[str, List[Dict[str, Any]]]:
    #     """ Renders interface facilitating minor layer-wise changes for an
    #         existing model architecture for a specific experiment submitted in
    #         a Synergos network

    #     Args:
    #         data (dict): Information relevant to a registered experiment
    #     Returns:
    #         Agumented architecture (dict)
    #     """
    #     architecture = data.get('model', [])
    #     layer_idxs = range(len(architecture))

    #     with st.beta_container():
    #         columns = st.beta_columns(2)

    #         with columns[0]:

    #             selected_layer_idx = st.selectbox(
    #                 label='Jump to layer:', 
    #                 options=layer_idxs
    #             )

    #             layer_info = architecture[selected_layer_idx]
    #             curr_is_input = layer_info.get('is_input', False)
    #             curr_l_type = layer_info.get('l_type', "")
    #             curr_structure = layer_info.get('structure', {})
    #             curr_activation = layer_info.get('activation', "")

    #         with columns[1]:

    #             updated_l_type = st.text_input(
    #                 label="Layer Type:",
    #                 value=curr_l_type,
    #                 key=f"layer_type_{selected_layer_idx}"
    #             )

    #             updated_structure_string = st.text_area(
    #                 label="Layer Parameters:",
    #                 value=json.dumps(curr_structure),
    #                 key=f"layer_structure_{selected_layer_idx}"
    #             )
    #             updated_structure = json.loads(updated_structure_string)

    #             updated_activation = st.text_input(
    #                 label="Layer Activation:",
    #                 value=curr_activation,
    #                 key=f"layer_activation_{selected_layer_idx}"
    #             ) 

    #             updated_layer = {
    #                 'is_input': curr_is_input,
    #                 'l_type': updated_l_type,
    #                 'structure': updated_structure,
    #                 'activation': updated_activation
    #             }

    #             is_previewed = st.checkbox(label="Preview layer changes")
    #             if is_previewed:
    #                 with st.echo(code_location="below"):
    #                     st.write(updated_layer)

    #         st.markdown("---")

    #     architecture[selected_layer_idx] = updated_layer

    #     return {'model': architecture}


    # def render_architecture_metadata(
    #     self, 
    #     data: Dict[str, Any] = {}
    # ) -> Dict[str, List[Dict[str, Any]]]:
    #     """ Renders a form capturing existing the model architecture to be
    #         used for a specified experiment registered in a deployed Synergos 
    #         network, given its prerequisite experiment information, as well as 
    #         any updates to their values.

    #     Args:
    #         data (dict): Information relevant to a registered experiment
    #     Returns:
    #         Updated architecture (dict)
    #     """
    #     composite_key = data.get('key', {})
    #     collab_id = composite_key.get('collab_id', "")
    #     project_id = composite_key.get('project_id', "")
    #     expt_id = composite_key.get('expt_id', "")

    #     model = data.get('model', [])

    #     with st.beta_container():

    #         with st.beta_container():
    #             left_column, right_column = st.beta_columns(2)

    #             with left_column:
    #                 is_previewed = st.checkbox(label="Preview architecture")

    #             with right_column:
    #                 if is_previewed:
    #                     with st.echo(code_location='below'):
    #                         st.write(model)

    #         with st.beta_container():
    #             left_column, right_column = st.beta_columns(2)

    #             with left_column:
    #                 is_downloaded = st.checkbox(label="Export architecture")
                
    #             with right_column:
    #                 if is_downloaded:
    #                     filename = st.text_input(
    #                         label="Filename:",
    #                         value=f"ARCH_{collab_id}_{project_id}_{expt_id}",
    #                         help="Specify a custom filename if desired"
    #                     )
    #                     is_pickled = st.checkbox('Save as pickle file')
    #                     download_name = (
    #                         f"{filename}.pkl" 
    #                         if is_pickled 
    #                         else f"{filename}.json"
    #                     )
    #                     download_tag = download_button(
    #                         object_to_download=model,
    #                         download_filename=download_name,
    #                         button_text="Download"
    #                     )
    #                     st.markdown(download_tag, unsafe_allow_html=True)

    #     return {'model': model}

    ##################
    # Core Functions #
    ##################

    # def display(
    #     self, 
    #     data: Dict[str, Any] = {}
    # ) -> Dict[str, List[Dict[str, Any]]]:
    #     """ Main wrapper encapsulating form design responsible for rendering
    #         all information captured in a registered experiment.

    #     Args:
    #         data (dict): Information relevant to a registered experiment
    #     Returns:
    #         Updated experiment info (dict)
    #     """
    #     if not data:
    #         return {}

    #     super().display(data, is_stacked=False)

    #     st.header("Model Architecture")
    #     updated_architecture = self.render_architecture_metadata(data)

    #     return updated_architecture


    # def modify(
    #     self, 
    #     data: Dict[str, Any] = {}
    # ) -> Dict[str, List[Dict[str, Any]]]:
    #     """ Main wrapper encapsulating form design responsible for rendering
    #         all information captured in a registered experiment.

    #     Args:
    #         data (dict): Information relevant to a registered experiment
    #     Returns:
    #         Updated experiment info (dict)
    #     """
    #     if not data:
    #         return {}

    #     super().display(data, is_stacked=False)

    #     mod_option = st.radio(
    #         "Select a modification:",
    #         options=MODIFICATION_OPTIONS
    #     )

    #     if mod_option == MODIFICATION_OPTIONS[1]:
    #         updated_architecture = self.render_minor_mods(data)

    #     else:
    #         updated_architecture = self.render_upload_mods()

    #     return updated_architecture