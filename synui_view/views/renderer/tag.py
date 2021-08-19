#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os
import random
from itertools import zip_longest
from pathlib import Path
from typing import Dict, List, Any

# Libs
import pydot
import streamlit as st

# Custom
from .base import BaseRenderer 

##################
# Configurations #
##################

###########
# Helpers #
###########

def generate_hex_colour(ex_prop: float = 10.0) -> str:
    """ Generates a random hex color sampled from a partitioned color space

    Args:
        ex_prop (float): Head & tail-end proportions to exclude from sampling.
            This is to make sure that the generated colours are of a certain
            distance away from white or black. Specified as a percentage.
    Returns:
        Random hex color (str)
    """
    MIN_COLOUR_VALUE = 0
    MAX_COLOUR_VALUE = 16777215
    
    final_min_value = int(MIN_COLOUR_VALUE + (ex_prop / 100 * MAX_COLOUR_VALUE))
    final_max_value = int(MAX_COLOUR_VALUE - (ex_prop / 100 * MAX_COLOUR_VALUE))
    random_number = random.randint(
        a=final_min_value,
        b=final_max_value
    )
    hex_number = str(hex(random_number))
    hex_number ='#'+ hex_number[2:]
    return hex_number

 
####################################
# Tag Renderer Class - TagRenderer #
####################################

class TagRenderer(BaseRenderer):
    """ Main class responsible for rendering tag-related forms in a streamlit 
        interface. 
    """
    def __init__(self):
        super().__init__()
        self._options = []
        self._selected_srcs = []

    ###########
    # Helpers #
    ###########

    def __parse_to_tags(
        self, 
        meta: str, 
        tag_string: str,
        signature: str = ""
    ) -> List[List[str]]:
        """ Acquires and convert declared paths to data sources into data tags 

        Args:
            meta (str): Type of data tags processed (i.e. 'train'/'evaluate'/'predict')
        Returns:
            Meta-specific Data tags (list)
        """           
        data_meta_paths = tag_string.splitlines()

        options_container = st.empty()
        self._options = options_container.multiselect(
            label=f"{meta.upper()} Data Sources:", 
            options=data_meta_paths, 
            default=data_meta_paths,
            key=f"{meta}_options_{signature}"
        )

        data_meta_tokens = [
            Path(path_str).parts[1:] 
            for path_str in self._options
        ]
        return data_meta_tokens


    def __parse_to_tree(self, meta: str, data_tags: List[List[str]]) -> None:
        """ Visualizes declared data tags for currrent meta type as a graph 

        Args:
            meta (str): Type of data tags processed (i.e. 'train'/'evaluate'/'predict')
            data_tags (list(list(str))): File path tokens declared for use
        """
        if data_tags:
            
            data_tree = pydot.Dot(
                f"{meta.upper()} Dataset Structure", 
                # graph_type='graph', 
                rankdir="LR",
                fillcolor="white",
                bgcolor="white"
            )
            data_tree.set_node_defaults(
                color='black',
                style='filled',
                shape='box',
                fontname='Arial',
                fontsize='15',
                fontcolor='white'
            )

            # Generate all nodes first
            node_colours = {}
            for idx, tags in enumerate(zip_longest(*data_tags)):

                # Generate unique colors for each token hierarchy
                curr_colour = node_colours.get(idx, generate_hex_colour())
                node_colours[idx] = curr_colour

                tags_keypoints = [tag for tag in set(tags) if tag]
                for idx, node_name in enumerate(tags_keypoints):

                    curr_node = pydot.Node(
                        node_name, 
                        label=node_name,
                        shape='rectangle',
                        style='filled',
                        color=curr_colour#"#DC582A"
                    )
                    data_tree.add_node(curr_node)

            for idx, tags in enumerate(data_tags):

                curr_edge_colour = generate_hex_colour()
                prev_node_name = data_tree.get_name()
                for node_name in tags:

                    # if not data_tree.get_edge(prev_node_name, node_name):
                    node_edge = pydot.Edge(
                        prev_node_name, 
                        node_name, 
                        color=curr_edge_colour
                    )
                    data_tree.add_edge(node_edge)

                    prev_node_name = node_name

            with st.beta_container():
                for _ in range(1):
                    st.markdown('')

                tree_png = data_tree.create_png()
                st.image(
                    tree_png, 
                    caption=f"{meta.upper()} Dataset Hierarchy",
                    use_column_width='always'
                )


    def render_tag_metadata(
        self, 
        data: Dict[str, Any] = {},
        signature: str = ""
    ) -> Dict[str, List[List[str]]]:
        """ Renders entry field for specifying dataset tags for use in 
            Synergos

        Returns:
            Tag details (dict)
        """
        TAG_KEYS = ["train", "evaluate", "predict"]

        with st.beta_container():
            columns = st.beta_columns((1,2))
            dataset_types = columns[0].multiselect(
                label="Select dataset type(s):",
                options=TAG_KEYS,
                default=TAG_KEYS,
                key=f"tag_keys_{signature}"
            )

            st.markdown("---")

        tag_details = {}
        for dataset_type in dataset_types:
            with st.beta_container():
                columns = st.beta_columns((1, 2))

                with columns[0]:
                    meta_tags = data.get(dataset_type, [])
                    meta_tag_paths = [
                        Path(*[os.sep, *tokens]).as_posix() 
                        for tokens in meta_tags
                    ]

                    updated_meta_string = st.text_area(
                        label=f"{dataset_type.upper()} tags options:", 
                        height=300,
                        value="\n".join(meta_tag_paths),
                        help=f"All {dataset_type.upper()} tag declarations must \
                        be made here.",
                        key=f"dataset_type_{dataset_type}_{signature}"
                    ).replace('\'', '"')

                    updated_meta_tags = self.__parse_to_tags(
                        meta=dataset_type,
                        tag_string=updated_meta_string,
                        signature=signature
                    )

                with columns[1]:
                    self.__parse_to_tree(
                        meta=dataset_type, 
                        data_tags=updated_meta_tags
                    )

                tag_details[dataset_type] = updated_meta_tags

                st.markdown("---")

        return tag_details

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

        super().display(data, is_stacked=False)  # fields are stacked by default

        st.header("Registered Datasets")
        updated_tags = self.render_tag_metadata(data)

        return updated_tags