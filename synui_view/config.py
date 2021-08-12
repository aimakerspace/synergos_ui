#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os
from pathlib import Path

# Libs


# Custom


##################
# Configurations #
##################

SRC_DIR = Path(__file__).parent.absolute()

API_VERSION = "0.2.0"

##############################################
# Synergos UI Container Local Configurations #
##############################################
"""
General parameters & constants
"""

# State static directory
STATIC_DIR = os.path.join(SRC_DIR, "static")

# State image directory
IMAGE_DIR = os.path.join(STATIC_DIR, "images")

# State styling directory
STYLES_DIR = os.path.join(STATIC_DIR, "styles")