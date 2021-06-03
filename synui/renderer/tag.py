#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import pprint
from typing import Dict, List, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 

##################
# Configurations #
##################


####################################
# Tag Renderer Class - TagRenderer #
####################################

class TagRenderer(BaseRenderer):
    """ Main class responsible for rendering tag-related forms in a streamlit 
        interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_tag_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, List[List[str]]]:
        """ Renders a form capturing dataset tags registered for use 
            under by a participant in a deployed Synergos network, given its 
            prerequisite information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a tag entry
        Returns:
            Updated data tags (dict)
        """     
        train_tags = data.get('train', [])
        valid_tags = data.get('evaluate', [])
        predict_tags = data.get('predict', [])

        with st.beta_container():
            updated_train_tags = st.text_area(
                label="Training Data Tags", 
                value=pprint.pformat(train_tags),
                height=200
            )
            updated_eval_tags = st.text_area(
                label="Evaluation Data Tags", 
                value=pprint.pformat(valid_tags),
                height=200
            )
            updated_predict_tags = st.text_area(
                label="Inference Data Tags", 
                value=pprint.pformat(predict_tags),
                height=200
            )

        return {
            'train': updated_train_tags,
            'evaluate': updated_eval_tags,
            'predict': updated_predict_tags
        }

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, List[List[str]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured regarding the dataset tags registered for 
            use under by a participant
            
        Args:
            data (dict): Information relevant to a tag entry
        Returns:
            Updated tag info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=True)

        st.header("Registered Datasets")
        updated_tags = self.render_tag_metadata(data)

        return updated_tags