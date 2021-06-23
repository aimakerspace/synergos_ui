#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os

# Libs
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Custom
from config import ASSETS_DIR
from synui.ui_collaboration import app as collab_app
from synui.ui_project import app as project_app
from synui.ui_experiment import app as expt_app
from synui.ui_run import app as run_app
from synui.ui_participant import app as participant_app
from synui.ui_registration import app as reg_app
from synui.landing import app as landing_app
from synui.submission import app as submit_app
from synui.utils import MultiApp

##################
# Configurations #
##################

FAVICON_PATH = os.path.join(ASSETS_DIR, "images", "Synergos-Favicon.ico")

PLACEHOLDER_OPTION = "Select an option"

SUPPORTED_ROLES = [PLACEHOLDER_OPTION, "Orchestrator", "Participant"]

SUPPORTED_DEFAULT_PROCESSES = {
    PLACEHOLDER_OPTION: landing_app, 
    "Construct a deployment script": None
}

SUPPORTED_ORCHESTRATOR_PROCESSES = {
    **SUPPORTED_DEFAULT_PROCESSES,
    "Manage collaboration(s)": collab_app,
    "Manage project(s)": project_app,
    "Manage experiment(s)": expt_app,
    "Manage run(s)": run_app,
    "Submit federated job(s)": submit_app,
    "Analyse federated job(s)": None,
    "Optimize a model": None
}

SUPPORTED_PARTICIPANT_PROCESSES = {
    **SUPPORTED_DEFAULT_PROCESSES,
    "Manage your profile": participant_app,
    "Manage your registrations": reg_app,
    "Submit inference(s)": None
}

######################################
# Main Synergos UI - Page formatting #
######################################

st.set_page_config(
    page_title="Synergos UI", 
    page_icon=FAVICON_PATH,
    layout="wide"
)

hide_streamlit_style = "<style>footer {visibility: hidden;}</style>"
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# resize_iframes_style = """
# <style>
#     iframe {
#         resize: both;
#         overflow: auto;
#     }
# </style>
# """
# st.markdown(resize_iframes_style, unsafe_allow_html=True) 


with st.sidebar.beta_container():

    st.header("OPTIONS")

    role = st.selectbox(
        label='What is your role?', 
        options=SUPPORTED_ROLES,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

if role == "Orchestrator":
    supported_processes = SUPPORTED_ORCHESTRATOR_PROCESSES

elif role == "Participant":
    supported_processes = SUPPORTED_PARTICIPANT_PROCESSES

else:
    supported_processes = {PLACEHOLDER_OPTION: landing_app}


multiapp = MultiApp()
for app_args in supported_processes.items():
    multiapp.add_app(*app_args)

multiapp.run()


# banner = """
#     <style>
#     body { 
#         margin: 0; 
#         font-family: Arial, Helvetica, sans-serif;
#     } 
#     .header {
#         padding: 10px 16px; 
#         background: #555; 
#         color: #f1f1f1; 
#         position: fixed; top:0;
#     } 
#     .sticky { 
#         position: fixed; 
#         top: 0; 
#         width: 100%;
#     } 
#     </style>
    
#     <div class="header" id="myHeader">
#     {1000}
#     </div>
# """



        # <!-- Option 1: Bootstrap Bundle with Popper -->
        # <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js" 
        #     integrity="sha384-p34f1UUtsS3wqzfto5wAAmdvj+osOnFyQFpp4Ua3gs/ZVWx6oOypYoCJhGGScy+8" 
        #     crossorigin="anonymous">
        # </script>
# Reference download button
# https://gist.github.com/chad-m/6be98ed6cf1c4f17d09b7f6e5ca2978f

# st.button('Hit me')
# st.checkbox('Check me out')
# st.radio('Radio', [1,2,3])
# st.selectbox('Select', [1,2,3])
# st.multiselect('Multiselect', [1,2,3])
# st.slider('Slide me', min_value=0, max_value=10)
# st.select_slider('Slide to select', options=[1,'2'])
# st.text_input('Enter some text')
# st.number_input('Enter a number')

# st.date_input('Date input')
# st.time_input('Time entry')
# st.file_uploader('File uploader')
# st.color_picker('Pick a color')

# # 
# kwargs = st.text_area('Area for textual entry')
# if kwargs:
#     st.write(json.loads(kwargs), type(kwargs))

# file = st.file_uploader("Pick a file")
# st.write(file)

# st.title('My first app')
# components.iframe(
#     src="http://localhost:8080/",
#     height=1000, 
#     scrolling=True    
# )

# components.iframe(
#     src="http://localhost:15672/",
#     height=920, 
#     scrolling=True    
# ) 

# components.iframe(
#     src="http://localhost:7400/",
#     height=1000, 
#     scrolling=True    
# )

# with st.beta_columns(2)[0]:
#     components.iframe(
#         src="http://localhost:5000/ttp/connect",
#         height=800, 
#         scrolling=True    
#     )

# download=st.button('Download Excel File')
# if download:
#     liste= ['A','B','C']
#     df_download= pd.DataFrame(liste)
#     df_download.columns=['Title']
#     csv = df_download.to_csv(index=False)
#     b64 = base64.b64encode(csv.encode()).decode()  # some strings
#     # linko= f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'
    
#     linko = f'<meta name="TEST.txt" http-equiv="refresh" content="0; url=data:file/txt;base64,{b64}">'
#     st.markdown(linko, unsafe_allow_html=True)


# df = pd.DataFrame({
#   'first column': [1, 2, 3, 4],
#   'second column': [10, 20, 30, 40]
# })

# df

# if st.checkbox('Show dataframe'):
#     chart_data = pd.DataFrame(
#        np.random.randn(20, 3),
#        columns=['a', 'b', 'c'])

#     chart_data

#     option = st.selectbox(
#         'Which number do you like best?',
#         df['first column'])

#     'You selected: ', option

# left_column, right_column = st.beta_columns(2)
# pressed = left_column.button('Press me?')
# if pressed:
#     right_column.write("Woohoo!")





# expander = st.beta_expander("FAQ")
# expander.write("Here you could put in some really, really long explanations...")

# date = st.date_input("Pick a date")
# number = st.slider("Pick a number", 0, 100)
# file = st.file_uploader("Pick a file")
# st.write(file)

# options = st.multiselect(
# 'What are your favorite colors',
# ['Green', 'Yellow', 'Red', 'Blue'],
# ['Yellow', 'Red'])

# st.write('You selected:', options)

# st.number_input('port declaration', value=8000, help="Something here")

# # ---------------------
# # Download from memory
# # ---------------------
# if st.checkbox('Download object from memory'):
#     st.write('~> Use if you want to save some data from memory (e.g. pd.DataFrame, dict, list, str, int)')

#     # Enter text for testing
#     s = st.selectbox('Select dtype', ['list',  # TODO: Add more
#                                         'str',
#                                         'int',
#                                         'float',
#                                         'dict',
#                                         'bool',
#                                         'pd.DataFrame'])
    
#     filename = st.text_input('Enter output filename and ext (e.g. my-dataframe.csv, my-file.json, my-list.txt)', 'my-file.json')

#     # Pickle Rick
#     pickle_it = st.checkbox('Save as pickle file')

#     sample_df = pd.DataFrame({'x': list(range(10)), 'y': list(range(10))})
#     sample_dtypes = {'list': [1,'a', [2, 'c'], {'b': 2}],
#                         'str': 'Hello Streamlit!',
#                         'int': 17,
#                         'float': 17.0,
#                         'dict': {1: 'a', 'x': [2, 'c'], 2: {'b': 2}},
#                         'bool': True,
#                         'pd.DataFrame': sample_df}

#     # Display sample data
#     st.write(f'#### Sample `{s}` to be saved to `{filename}`')
#     st.code(sample_dtypes[s], language='python')

#     # Download sample
#     download_button_str = download_button(sample_dtypes[s], filename, f'Click here to download {filename}', pickle_it=pickle_it)
#     st.markdown(download_button_str, unsafe_allow_html=True)

#     if st.checkbox('Show code example '):
#         code_text = f"""
#                     s = {sample_dtypes[s]}
#                     download_button_str = download_button(s, '{filename}', 'Click here to download {filename}', pickle_it={pickle_it})
#                     st.markdown(download_button_str, unsafe_allow_html=True)"""

#         st.code(code_text, language='python')