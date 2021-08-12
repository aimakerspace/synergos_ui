#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os

# Libs
import streamlit as st
import streamlit.components.v1 as components

# Custom
from config import IMAGE_DIR
from views.utils import render_png

##################
# Configurations #
##################

ORCHESTRATOR_ICON_PATH = os.path.join(IMAGE_DIR, "orchestrator.png")
# OVERVIEW_PATH = os.path.join(ASSETS_DIR, "images", "Synergos-Overview.png")


##########################################
# Main Synergos UI Option - Landing Page #
##########################################

def introduce():
    """
    """
    st.title("What is Synergos?")

    # st.markdown("""
    #     Synergos is essentially a distributed system, in which different parties
    #     work together to train a machine learning model without exposing the 
    #     data of each individual party. The diagram below shows a single-party 
    #     view of Synergos’ key components.
    # """)
    # st.image(
    #     image=OVERVIEW_PATH, 
    #     caption="",
    #     use_column_width="always"
    # )
    # st.write("""
    #     For an indepth dive into each component, please refer to this 
    #     [article](https://makerspace.aisingapore.org/2020/11/a-peek-into-synergos-ai-singapores-federated-learning-system/).
    # """)

##########################################
# Main Synergos UI Option - Landing Page #
##########################################

def explain():
    """
    """
    st.title("How does Synergos work?")

################################
# Landing UI - Page Formatting #
################################

def app():
    """
    """
    pass