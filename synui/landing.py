#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os
from PIL import Image

# Libs
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Custom
from config import ASSETS_DIR
from synergos import Driver
from synui.utils import render_svg

##################
# Configurations #
##################

LOGO_PATH = os.path.join(ASSETS_DIR, "images", "Synergos-Logo.svg")
OVERVIEW_PATH = os.path.join(ASSETS_DIR, "images", "Synergos-Overview.png")


##########################################
# Main Synergos UI Option - Landing Page #
##########################################

def introduce():
    """
    """
    st.title("What is Synergos?")

    st.markdown("""
        Synergos is essentially a distributed system, in which different parties
        work together to train a machine learning model without exposing the 
        data of each individual party. The diagram below shows a single-party 
        view of Synergos’ key components.
    """)
    st.image(
        image=OVERVIEW_PATH, 
        caption="",
        use_column_width="always"
    )
    st.write("""
        For an indepth dive into each component, please refer to this 
        [article](https://makerspace.aisingapore.org/2020/11/a-peek-into-synergos-ai-singapores-federated-learning-system/).
    """)

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
    image_container = st.beta_container()
    _, mid_column, _ = image_container.beta_columns(3)
    render_svg(svg_path=LOGO_PATH, column=mid_column)

    intro_expander = st.beta_expander("Introduction")
    with intro_expander:
        introduce()

    architecture_expander = st.beta_expander("Architecture")
    with architecture_expander:
        explain()
