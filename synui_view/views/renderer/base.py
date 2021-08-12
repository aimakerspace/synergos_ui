#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import uuid
from typing import Dict, Any

# Libs
import streamlit as st

# Custom
from .abstract import AbstractRenderer 

##################
# Configurations #
##################



######################################
# Base Renderer Class - BaseRenderer #
######################################

class BaseRenderer(AbstractRenderer):
    """

    Attributes:
        _display_map (OrderedDict): 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_record_metadata(
        self, 
        data: Dict[str, Any] = {},
        is_stacked: bool = False
    ) -> Dict[str, str]:
        """ Renders a form capturing existing record metadata used for internal
            archival cataloging. Such metadata includes a uniquely generated ID
            and the type of document being rendered

        Args:
            data (dict): Information relevant to a relevant archival record
        Returns:
            Document metadata (dict)
        """
        doc_id = data.get('doc_id', "")
        kind = data.get('kind', "")

        with st.beta_container():
            columns = [st] if is_stacked else st.beta_columns(2)

            columns[0].text_input(
                label="Document ID:",
                value=doc_id,
                key=uuid.uuid4(),
                help=f"Unique ID used to internal {kind} cataloging"
            )
            columns[-1].text_input(
                label="Document Kind:",
                value=kind,
                key=uuid.uuid4(),
                help="Document type of current entry"
            )

            st.markdown("---")
        
        return {'doc_id': doc_id, 'kind': kind}

    ##################        
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {},
        is_stacked: bool = False
    ) -> Dict[str, str]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in any record.

        Args:
            data (dict): Information relevant to a record
        Returns:
            Record metadata (dict)           
        """
        return self.render_record_metadata(data, is_stacked=is_stacked)