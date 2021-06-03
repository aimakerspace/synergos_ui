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


################################################
# Alignment Renderer Class - AlignmentRenderer #
################################################

class AlignmentRenderer(BaseRenderer):
    """ Main class responsible for rendering alignment-related forms in a
        streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_alignment_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[str, Dict[str, List[Any]]]]:
        """ Renders a form capturing alignments detected for use required for a
            specific participant in a deployed Synergos network, given its 
            prerequisite information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Updated registration (dict)
        """         
        train_alignment_idxs = data.get('train', [])
        valid_alignment_idxs = data.get('evaluate', [])
        predict_alignment_idxs = data.get('predict', [])

        with st.beta_container():
            updated_train_alignment_idxs = st.text_area(
                label="Training Alignment Indexes:", 
                value=pprint.pformat(train_alignment_idxs),
                height=200
            )
            updated_valid_alignment_idxs = st.text_area(
                label="Evaluation Alignment Indexes:", 
                value=pprint.pformat(valid_alignment_idxs),
                height=200
            )
            updated_predict_alignment_idxs = st.text_area(
                label="Inference Alignment Indexes:", 
                value=pprint.pformat(predict_alignment_idxs),
                height=200
            )

        return {
            'train': updated_train_alignment_idxs,
            'evaluate': updated_valid_alignment_idxs,
            'predict': updated_predict_alignment_idxs
        }

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[str, Dict[str, List[Any]]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registered participant.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated participant info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=True)

        st.header("Dataset Alignments")
        updated_alignments = self.render_alignment_metadata(data)

        return updated_alignments