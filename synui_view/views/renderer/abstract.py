#!/usr/bin/env python

####################
# Required Modules #
####################


# Generic/Built-in
import abc
from typing import Dict

# Libs


# Custom


##################
# Configurations #
##################


##############################################
# Abstract Renderer Class - AbstractRenderer #
##############################################

class AbstractRenderer(abc.ABC):

    @abc.abstractmethod
    def display(self):
        """ Displays a series of renderable sequences in a Streamlit app """
        pass
