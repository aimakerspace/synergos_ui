#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from typing import Dict, List, Union, Any

# Libs
import streamlit as st

# Custom
from .base import BaseRenderer 
from .utils import render_svg

##################
# Configurations #
##################


####################################################
# Participant Renderer Class - ParticipantRenderer #
####################################################

class ParticipantRenderer(BaseRenderer):
    """ Main class responsible for rendering participant-related forms in
        a streamlit interface. 
    """
    def __init__(self):
        super().__init__()

    ###########
    # Helpers #
    ###########

    def render_profile_pic(self, data: Dict[str, Any] = {}):
        """ Renders a form capturing existing profile picture(s) registered 
            under a participant in a deployed Synergos network, given their 
            prerequisite metadata, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated profile picture (dict)
        """
        profile_pic = data.get('profile', "")

        # with st.beta_container():
        #     _, mid_column, _ = st.beta_columns(3)

        #     with mid_column:   
        #         render_svg("./assets/images/Synergos-Logo.svg")
        render_svg("./assets/images/Synergos-Logo.svg")


    def render_profile_summary(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, str]:
        """ Renders a form capturing existing descriptions of a participant in 
            a deployed Synergos network, given their prerequisite metadata, as 
            well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated profile description (dict)
        """
        summary = data.get('summary', "")

        with st.beta_container(): 
            updated_description = st.text_area(
                label="Description:", 
                value=summary
            )

        return {'summary': updated_description}


    def render_profile_categories(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, List[str]]:
        """ Renders a form capturing existing categories of interest/expertise
            registered under a participant in a deployed Synergos network, 
            given their prerequisite metadata, as well as any updates to their 
            values.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated profile categories (dict)
        """
        categories = data.get('category', [])

        with st.beta_container():
            updated_categories = st.multiselect(
                label="Categories:", 
                options=categories,
                default=categories,
                help="Participant's domain of expertise"
            )

        return {'category': updated_categories}


    def render_contact_details(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, str]:
        """ Renders a form capturing existing contact details registered under 
            a participant in a deployed Synergos network, given their 
            prerequisite metadata, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated contact details (dict)
        """
        email = data.get('email', "")
        phone = data.get('phone', "")

        with st.beta_container():   
            updated_email = st.text_input(label="Email:", value=email)
            updated_phone = st.text_input(label="Phone:", value=phone)

        return {'email': updated_email, 'phone': updated_phone}


    def render_profile_socials(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, str]]:
        """ Renders a form capturing existing social links registered under a
            participant in a deployed Synergos network, given their 
            prerequisite metadata, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated social metadata (dict)
        """
        socials = data.get('socials', {})

        website_url = socials.get('website', "")
        facebook_url = socials.get('facebook', "")
        linkedin_url = socials.get('linkedin', "")

        with st.beta_container():
            updated_website_url = st.text_input(
                label="Website:", 
                value=website_url
            )
            updated_facebook_url = st.text_input(
                label="Facebook:", 
                value=facebook_url
            )
            updated_linkedin_url = st.text_input(
                label="LinkedIn:", 
                value=linkedin_url
            )

        return {
            'socials': {
                'website': updated_website_url,
                'facebook': updated_facebook_url,
                'linkedin': updated_linkedin_url
            }
        }

    ##################
    # Core Functions #
    ##################

    def display(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        """ Main wrapper encapsulating form design responsible for rendering
            all information captured in a registered participant.

        Args:
            data (dict): Information relevant to a registered participant
        Returns:
            Updated participant info (dict)
        """
        if not data:
            return {}

        super().display(data, is_stacked=False)

        st.title("Participant Info")
        with st.beta_container():

            columns = st.beta_columns((1, 1.5))

            # with columns[0]:
            #     self.render_profile_pic(data)

            with columns[1]:
                st.header("**Profile**")
                updated_description = self.render_profile_summary(data)
                updated_categories = self.render_profile_categories(data)
                
                st.markdown("---")

                st.header("**Contacts**")   
                updated_contact_details = self.render_contact_details(data)

                st.markdown("---")

                st.header("**Socials**")
                updated_socials = self.render_profile_socials(data)

                st.markdown("---")

        return {
            **updated_description, 
            **updated_categories,
            **updated_contact_details,
            **updated_socials
        }


    def modify(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        """
        """
        pass