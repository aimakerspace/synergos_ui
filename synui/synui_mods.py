def app():
    """
    """
    st.title("Orchestrator: Create Collaboration(s)")

    basic_input_container = st.beta_container()
    left_column, right_column = basic_input_container.beta_columns(2)

    collab_id = left_column.text_input(
        label="Collaboration ID:",
        help="Declare the name of your new collaboration."
    )

    synergos_variant = right_column.selectbox(
        label="Variant:",
        options=list(DEFAULT_DEPLOYMENTS.keys()),
        help="Declare which variant of Synergos you deployed for this collaboration."
    )

    ##############################################################
    # Step 1: Connect Synergos Driver to a deployed orchestrator #
    ############################################################## 

    orchestrator_type = (1 if synergos_variant == "SynCluster" else 0)
    orchestrator_deployed = left_column.radio(
        label="Orchestrator Type", 
        options=["TTP", "Director"],
        index=orchestrator_type,
        help="Orchestrator type will be dynamically inferred given your specified variant."
    )
    orchestrator_host = right_column.text_input(
        label="Orchestrator IP:",
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = right_column.text_input(
        label="Orchestrator Port:",
        help="Declare the access port of your selected orchestrator."
    )
    driver = Driver(host=orchestrator_host, port=orchestrator_port)

    ##############################################################
    # Step 2: Connect Synergos Driver to a deployed orchestrator #
    ############################################################## 

    optional_components_deployed = st.multiselect(
        label="Supplementary components deployed for collaboration:", 
        options=[
            "Synergos Catalogue",
            "Synergos Logger",
            "Synergos Meter",
            "Synergos MLOps",
            "Synergos MQ",
            "Synergos UI"
        ], 
        default=DEFAULT_DEPLOYMENTS[synergos_variant],
        help="Declare which Addons were deployed alongside the core components."
    )

    # with st.form("collab_declaration"):

    component_input_container = st.beta_container()
    left_column, right_column = component_input_container.beta_columns(2)
    for idx, component in enumerate(optional_components_deployed):

        column = left_column #if idx % 2 else right_column

        column.header(f"Register specs for {component}:")
        
        host = column.text_input(label=f"Server IP for {component}:")
        if component == "Synergos Catalogue":
            catalogue_ui_port = column.number_input(
                label="Catalogue UI Port:", 
                value=6000
            )

        elif component == "Synergos Logger":
            sysmetrics_port = column.number_input(
                label="Sysmetrics Port:", 
                value=9100
            )
            director_port = column.number_input(
                label="Director Port:", 
                value=9200
            )
            ttp_port = column.number_input(
                label="TTP Port:", 
                value=9300
            )
            worker_port = column.number_input(
                label="Worker Port:", 
                value=9400
            )

        elif component == "Synergos Meter":
            meter_port = column.number_input(
                label="Meter Port:", 
                value=7000
            )

        elif component == "Synergos MLOps":
            mlops_port = column.number_input(
                label="MLOps Port:", 
                value=7000
            )

        elif component == "Synergos MQ":
            mq_port = column.number_input(
                label="MQ Port:", 
                value=7000
            )

        elif component == "Synergos UI":
            ui_port = column.number_input(
                label="UI Port:", 
                value=7000
            )


        # # Every form must have a submit button.
        # submitted = st.form_submit_button("Submit")















def browse_collaborations():
    """
    """
    st.title("Orchestrator - Browse Existing Collaboration(s)")

    ########################
    # Step 0: Introduction #
    ########################

    collab_id = st.text_input(
        label="Collaboration ID:",
        help="Declare the name of your new collaboration."
    )

    basic_input_container = st.beta_container()
    left_column, mid_column, right_column = basic_input_container.beta_columns(3)

    orchestrator_deployed = left_column.selectbox(
        label="Orchestrator Type", 
        options=["TTP", "Director"],
        help="Orchestrator type will be dynamically inferred given your specified variant."
    )

    orchestrator_host = mid_column.text_input(
        label="Orchestrator IP:",
        # value=default_host,
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = right_column.number_input(
        label="Orchestrator Port:",
        value=5000,
        help="Declare the access port of your selected orchestrator."
    )
    collab_driver = Driver(host=orchestrator_host, port=orchestrator_port)

    if collab_id:
        ###########################################################
        # Step 1: Retrieve all Collaboration details (if present) #
        ########################################################### 

        ########################################################################
        # Step 2: List out all job associations registered under collaboration #
        ########################################################################

        st.header("Job Associations")

        association_container = st.beta_container()
        left_column, mid_column, right_column = association_container.beta_columns(3)

        project_resp = collab_driver.projects.read_all(collab_id=collab_id)
        project_data = project_resp['data']
        project_ids = [project['key']['project_id'] for project in project_data]
        selected_project_id = left_column.selectbox("Project:", options=project_ids)

        expt_resp = collab_driver.experiments.read_all(
            collab_id=collab_id, 
            project_id=selected_project_id
        )
        expt_data = expt_resp['data']
        expt_ids = [expt['key']['expt_id'] for expt in expt_data]
        selected_expt_id = left_column.selectbox("Experiment:", options=expt_ids)






        project_expander = st.beta_expander("Projects")
        with project_expander:
            render_projects(driver=collab_driver, collab_id=collab_id)

        experiment_expander = st.beta_expander("Experiments")
        with experiment_expander:
            render_experiments()

        run_expander = st.beta_expander("Runs")
        with run_expander:
            render_runs()

        registration_expander = st.beta_expander("Registrations")
        with registration_expander:
            render_registrations()











def render_collaborations(driver: Driver = None):
    """ Renders out retrieved collaboration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
    Returns:
        Selected collaboration ID  
    """
    if driver:
        collab_data = driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in collab_data]
    else:
        collab_ids = []

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="""Select a collaboration to peruse."""
        )

        if driver:
            selected_collab_data = driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
    
            if selected_collab_data:
                
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    doc_id = selected_collab_data.get('doc_id', "")
                    kind = selected_collab_data.get('kind', "")
                    left_column.text_input(
                        label=f"Document ID:",
                        value=doc_id,
                        help=f"Unique ID used to internal collaboration cataloging"
                    )
                    right_column.text_input(
                        label=f"Document Kind:",
                        value=kind,
                        help=f"Document type of current entry"
                    )

                st.header("Collaboration Components")

                # Render Synergos Catalogue Metadata
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    catalogue_host = selected_collab_data.get('catalogue_host', "")
                    catalogue_port = selected_collab_data.get('catalogue_port', 0)
                    left_column.text_input(
                        label=f"Server IP for Synergos Catalogue:",
                        value=catalogue_host,
                        help=f"Registered server IP where Synergos Catalogue is hosted"
                    )
                    right_column.number_input(
                        label=f"Server Port for Synergos Catalogue:",
                        value=catalogue_port,
                        help=f"Registered server port to access Synergos Catalogue"
                    )

                # Render Synergos Logger Metadata
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    logger_host = selected_collab_data.get('logger_host', "")
                    logger_ports = selected_collab_data.get('logger_ports', {})

                    sysmetrics_port = logger_ports.get('sysmetrics', 0)
                    director_port = logger_ports.get('director', 0)
                    ttp_port = logger_ports.get('ttp', 0)
                    worker_port = logger_ports.get('worker', 0)

                    left_column.text_input(
                        label=f"Server IP for Synergos Logger:",
                        value=logger_host,
                        help=f"Registered server IP where Synergos Logger is hosted"
                    )

                    right_column.number_input(
                        label=f"Sysmetrics Port for Synergos Logger:",
                        value=sysmetrics_port,
                        help=f"Registered Sysmetric port to access Synergos Logger"
                    )
                    right_column.number_input(
                        label=f"Director Port for Synergos Logger:",
                        value=director_port,
                        help=f"Registered director port to access Synergos Logger"
                    )
                    right_column.number_input(
                        label=f"TTP Port for Synergos Logger:",
                        value=ttp_port,
                        help=f"Registered TTP port to access Synergos Logger"
                    )
                    right_column.number_input(
                        label=f"Worker Port for Synergos Logger:",
                        value=worker_port,
                        help=f"Registered worker port to access Synergos Logger"
                    )

                # Render Synergos Meter Metadata
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    meter_host = selected_collab_data.get('meter_host', "")
                    meter_port = selected_collab_data.get('meter_port', 0)
                    left_column.text_input(
                        label=f"Server IP for Synergos Meter:",
                        value=meter_host,
                        help=f"Registered server IP where Synergos Meter is hosted"
                    )
                    right_column.number_input(
                        label=f"Server Port for Synergos Meter:",
                        value=meter_port,
                        help=f"Registered server port to access Synergos Meter"
                    )

                # Render Synergos MLOps Metadata
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    mlops_host = selected_collab_data.get('mlops_host', "")
                    mlops_port = selected_collab_data.get('mlops_port', 0)
                    left_column.text_input(
                        label=f"Server IP for Synergos MLOps:",
                        value=mlops_host,
                        help=f"Registered server IP where Synergos MLOps is hosted"
                    )
                    right_column.number_input(
                        label=f"Server Port for Synergos MLOps:",
                        value=mlops_port,
                        help=f"Registered server port to access Synergos MLOps"
                    )

                # Render Synergos MQ Metadata
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    mq_host = selected_collab_data.get('mq_host', "")
                    mq_port = selected_collab_data.get('mq_port', 0)
                    left_column.text_input(
                        label=f"Server IP for Synergos MQ:",
                        value=mq_host,
                        help=f"Registered server IP where Synergos MQ is hosted"
                    )
                    right_column.number_input(
                        label=f"Server Port for Synergos MQ:",
                        value=mq_port,
                        help=f"Registered server port to access Synergos MQ"
                    )

                # Render Synergos UI Metadata
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    ui_host = selected_collab_data.get('ui_host', "")
                    ui_port = selected_collab_data.get('ui_port', 0)
                    left_column.text_input(
                        label=f"Server IP for Synergos UI:",
                        value=ui_host,
                        help=f"Registered server IP where Synergos UI is hosted"
                    )
                    right_column.number_input(
                        label=f"Server Port for Synergos UI:",
                        value=ui_port,
                        help=f"Registered server port to access Synergos UI"
                    )

    return selected_collab_id



def render_projects(driver: Driver = None, collab_id: str = ""):
    """ Renders out retrieved project metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
    Returns:
        Selected project ID  
    """
    if driver and collab_id:
        project_data = driver.projects.read_all(collab_id).get('data', [])
        project_ids = [proj['key']['project_id'] for proj in project_data]
    else:
        project_ids = []

    with st.beta_container():

        selected_project_id = st.selectbox(
            label="Project ID:", 
            options=project_ids,
            help="""Select a project to peruse."""
        )

        if driver:
            selected_project_data = driver.projects.read(
                collab_id=collab_id,
                project_id=selected_project_id
            ).get('data', {})
        else:
            selected_project_data = {}

        if selected_project_data:
            selected_project_data.pop('relations')  # no relations rendering

        with st.beta_expander("Project Details"):
                
            if selected_project_data:

                doc_id = selected_project_data.get('doc_id', "")
                kind = selected_project_data.get('kind', "")
                action = selected_project_data.get('action', "")
                incentives = selected_project_data.get('incentives', {})

                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    left_column.text_input(
                        label="Document ID:",
                        value=doc_id,
                        help=f"Unique ID used to internal project cataloging"
                    )
                    right_column.text_input(
                        label="Document Kind:",
                        value=kind,
                        help=f"Document type of current entry"
                    )

                st.header("Project Metadata")
                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    left_column.text_input(
                        label="Action:",
                        value=action,
                        help="Type of ML action to perform on the dataset pool"
                    )
                    right_column.text_area(
                        label="Incentives:",
                        value=incentives,
                        help="Incentive hierarchy to be applied on the project"
                    )

    return selected_project_id





def render_experiments(
    driver: Driver = None, 
    collab_id: str = "", 
    project_id: str = ""
):
    """ Renders out retrieved experiment metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
    Returns:
        Selected experiment ID  
    """
    if driver:
        expt_data = driver.experiments.read_all(
            collab_id=collab_id, 
            project_id=project_id
        ).get('data', [])
        expt_ids = [expt['key']['expt_id'] for expt in expt_data]
    else:
        expt_ids = []
    
    with st.beta_container():

        selected_expt_id = st.selectbox(
            label="Experiment ID:", 
            options=expt_ids,
            help="""Select an experiment to peruse."""
        )

        if driver:
            selected_expt_data = driver.experiments.read(
                collab_id=collab_id,
                project_id=project_id,
                expt_id=selected_expt_id
            ).get('data', {})
        else:
            selected_expt_data = {}
            
        if selected_expt_data:
            selected_expt_data.pop('relations')  # no relations rendering

        with st.beta_expander("Experiment Details"):

            if selected_expt_data:              

                doc_id = selected_expt_data.get('doc_id', "")
                kind = selected_expt_data.get('kind', "")
                model = selected_expt_data.get('model', [])

                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    left_column.text_input(
                        label="Document ID:",
                        value=doc_id,
                        help=f"Unique ID used to internal experiment cataloging"
                    )
                    right_column.text_input(
                        label="Document Kind:",
                        value=kind,
                        help=f"Document type of current entry"
                    )

                with st.beta_container():

                    st.header("Model Architecture")

                    with st.beta_container():
                        left_column, right_column = st.beta_columns(2)

                        with left_column:
                            is_previewed = st.checkbox(label="Preview architecture")

                        with right_column:
                            if is_previewed:
                                with st.echo(code_location='below'):
                                    st.write(model)

                    with st.beta_container():
                        left_column, right_column = st.beta_columns(2)

                        with left_column:
                            is_downloaded = st.checkbox(label="Export architecture")
                        
                        with right_column:
                            if is_downloaded:
                                filename = st.text_input(
                                    label="Filename:",
                                    value=f"MODEL_{collab_id}_{project_id}_{selected_expt_id}",
                                    help="Specify a custom filename if desired"
                                )
                                is_pickled = st.checkbox('Save as pickle file')
                                download_name = (
                                    f"{filename}.pkl" 
                                    if is_pickled 
                                    else f"{filename}.json"
                                )
                                download_tag = download_button(
                                    object_to_download=model,
                                    download_filename=download_name,
                                    button_text="Download"
                                )
                                st.markdown(download_tag, unsafe_allow_html=True)

    return selected_expt_id






def render_runs(
    driver: Driver = None, 
    collab_id: str = "", 
    project_id: str = "",
    expt_id: str = ""
):
    """ Renders out retrieved experiment metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
        expt_id (str): ID of selected experiment to be rendered
    Returns:
        Selected experiment ID
    """
    if driver:
        run_data = driver.runs.read_all(
            collab_id=collab_id, 
            project_id=project_id,
            expt_id=expt_id
        ).get('data', [])
        run_ids = [run['key']['run_id'] for run in run_data]
    else:
        run_ids = []
    
    with st.beta_container():

        selected_run_id = st.selectbox(
            label="Run ID:", 
            options=run_ids,
            help="""Select an run to peruse."""
        )

        if driver:
            selected_run_data = driver.runs.read(
                collab_id=collab_id,
                project_id=project_id,
                expt_id=expt_id,
                run_id=selected_run_id
            ).get('data', {})
        else:
            selected_run_data = {}

        if selected_run_data:
            selected_run_data.pop('relations')  # no relations rendering
        
        with st.beta_expander("Run Details"):

            if selected_run_data:

                doc_id = selected_run_data.pop('doc_id')
                kind = selected_run_data.pop('kind')

                selected_run_data.pop('key')

                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    left_column.text_input(
                        label="Document ID:",
                        value=doc_id,
                        help=f"Unique ID used to internal run cataloging"
                    )
                    right_column.text_input(
                        label="Document Kind:",
                        value=kind,
                        help=f"Document type of current entry"
                    )

                st.header("Hyperparameters")

                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    with left_column:
                        is_previewed = st.checkbox(label="Preview hyperparameters")

                    with right_column:
                        if is_previewed:
                            with st.echo(code_location='below'):
                                st.write(selected_run_data)

                with st.beta_container():
                    left_column, right_column = st.beta_columns(2)

                    with left_column:
                        is_downloaded = st.checkbox(label="Export hyperparmeters")
                    
                    with right_column:
                        if is_downloaded:
                            filename = st.text_input(
                                label="Filename:",
                                value=f"RUN_{collab_id}_{project_id}_{expt_id}_{selected_run_id}",
                                help="Specify a custom filename if desired"
                            )
                            is_pickled = st.checkbox(
                                label='Save as pickle file',
                                key=uuid.uuid4()
                            )
                            download_name = (
                                f"{filename}.pkl" 
                                if is_pickled 
                                else f"{filename}.json"
                            )
                            download_tag = download_button(
                                object_to_download=selected_run_data,
                                download_filename=download_name,
                                button_text="Download"
                            )
                            st.markdown(download_tag, unsafe_allow_html=True)

    return selected_run_id



    def render_project_metadata(self, data: List[Dict[str, Any]] = []):
        """ 
        """
        action = data.get('action', "")
        incentives = data.get('incentives', {})

        with st.beta_container():
            left_column, right_column = st.beta_columns(2)

            left_column.text_input(
                label="Action:",
                value=action,
                help="Type of ML action to perform on the dataset pool"
            )
            right_column.text_area(
                label="Incentives:",
                value=pprint.pformat(incentives),
                height=200,
                help="Incentive hierarchy to be applied on the project"
            )

        return action, incentives






    def show_display_sequence(self) -> List:
        """

        Returns:
            Display sequence (list)
        """
        return [seq_info for _, seq_info in sorted(self._display_map.items())]


    def add_sequence(self, level: int, f_name: str, f_seq: Callable):
        """

        Args:
            level (int): Document hierarchy to order renders
            f_name (str): Name of Streamlit widget cluster to render
            f_seq (Callable): Function encapsulating Streamlit widget instantiations
        """        
        if level not in self._display_map.keys():
            self._display_map.update({level: (f_name, f_seq)})
        else:
            raise RuntimeError("Current level is already occupied! Use '.update_sequence()' instead.")


    def update_sequence(self, level: int, f_name: str, f_seq: Callable):
        """

        Args:
            level (int): Document hierarchy to order renders
            f_name (str): Name of Streamlit widget cluster to render
            f_seq (Callable): Function encapsulating Streamlit widget instantiations
        """
        if level in self._display_map.keys():
            self._display_map.update({level: (f_name, f_seq)})
        else:
            raise RuntimeError("Specified level does not exist! Use '.add_sequence()' instead.")
    

    def delete_level(self, level: int) -> Tuple[str, Callable]:
        """

        Args:
            level (int): Display layer targetted for deletion
        Returns:
            Deleted sequence (tuple(str, callable))
        """
        try:
            deleted_seq = self._display_map.pop(level)
            return deleted_seq
        except KeyError:
            raise RuntimeError("Targetted level does not exist!")


    def delete_sequence(self, f_name: str) -> Tuple[str, Callable]:
        """

        Args:
            f_name (int): Name of Streamlit widget cluster to be deleted
        Returns:
            Deleted sequence (tuple(str, callable))
        """
        for curr_level, (curr_f_name, curr_f_seq) in self._display_map.items():
            if curr_f_name == f_name:
                 return self.delete_level(level=curr_level)
        
        # If no such widget cluster exists, raise Exception!
        raise RuntimeError("Targetted widget cluster does not exist!")


    def display(self) -> Dict[str, Dict[str, Union[int, float, str]]]:
        """

        Returns:
            Output variables of all display sequences (dict)
        """
        display_seq = self.show_display_sequence()

        output_variables = {}
        for f_name, f_seq in display_seq:
            results = f_seq()
            output_variables[f_name] = {nameof(var): var for var in results}

        return output_variables










def create_collaborations():
    """ Main function that governs the creation of collaborations within a
        specified Synergos network
    """
    st.title("Orchestrator - Create New Collaboration(s)")

    ########################
    # Step 0: Introduction #
    ########################

    basic_input_container = st.beta_container()
    left_column, mid_column, right_column = basic_input_container.beta_columns(3)

    collab_id = left_column.text_input(
        label="Collaboration ID:",
        help="Declare the name of your new collaboration."
    )

    synergos_variant = mid_column.selectbox(
        label="Variant:",
        options=list(DEFAULT_DEPLOYMENTS.keys()),
        help="Declare which variant of Synergos you deployed for this collaboration."
    )

    deployment_mode = right_column.selectbox(
        label="Mode:",
        options=["local", "distributed"],
        help="""Declare which setting was Synergos deployed in. Selecting 
        'local' indicates that all components have been deployed onto the same 
        server. Conversely, selecting 'distributed' indicates a more complex
        network deployed."""
    )

    default_host = "localhost" if deployment_mode == 'local' else ""

    ##############################################################
    # Step 1: Connect Synergos Driver to a deployed orchestrator #
    ############################################################## 

    st.header("Step 1: Connect to your Orchestrator")
    driver_input_container = st.beta_container()
    left_column, right_column = driver_input_container.beta_columns(2)

    orchestrator_options = ["TTP" if synergos_variant != "SynCluster" else "Director"]
    orchestrator_deployed = left_column.selectbox(
        label="Orchestrator Type", 
        options=orchestrator_options,
        help="Orchestrator type will be dynamically inferred given your specified variant."
    )
    orchestrator_host = right_column.text_input(
        label="Orchestrator IP:",
        value=default_host,
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = right_column.number_input(
        label="Orchestrator Port:",
        value=5000,
        help="Declare the access port of your selected orchestrator."
    )
    driver = Driver(host=orchestrator_host, port=orchestrator_port)

    ###########################################
    # Step 2: Declare all deployed components #
    ########################################### 

    st.header("Step 2: Declare all components of your Synergos Network")

    optional_components_deployed = st.multiselect(
        label="Supplementary components deployed for collaboration:", 
        options=[
            "Synergos Catalogue",
            "Synergos Logger",
            "Synergos Meter",
            "Synergos MLOps",
            "Synergos MQ",
            "Synergos UI"
        ], 
        default=DEFAULT_DEPLOYMENTS[synergos_variant],
        help="Declare which Addons were deployed alongside the core components."
    )

    collab_task = driver.collaborations
    for idx, component in enumerate(optional_components_deployed, start=1):

        st.markdown(f"{idx}. Register specs for {component}:")
        
        component_input_container = st.beta_container()
        left_column, right_column = component_input_container.beta_columns(2)

        host = left_column.text_input(
            label=f"Server IP for {component}:",
            value=default_host,
            help=f"Declare server IP where {component} is hosted"
        )
        if component == "Synergos Catalogue":
            port = right_column.number_input(
                label=f"Port for {component}:", 
                value=6000
            )
            collab_task.configure_catalogue(host=host, port=port)

        elif component == "Synergos Logger":
            sysmetrics_port = right_column.number_input(
                label="Sysmetrics Port:", 
                value=9100
            )
            director_port = right_column.number_input(
                label="Director Port:", 
                value=9200
            )
            ttp_port = right_column.number_input(
                label="TTP Port:", 
                value=9300
            )
            worker_port = right_column.number_input(
                label="Worker Port:", 
                value=9400
            )
            collab_task.configure_logger(
                host=host, 
                sysmetrics_port=sysmetrics_port,
                director_port=director_port,
                ttp_port=ttp_port,
                worker_port=worker_port
            )

        elif component == "Synergos Meter":
            meter_port = right_column.number_input(
                label="Meter Port:", 
                value=10000
            )
            collab_task.configure_meter(host=host, port=meter_port)

        elif component == "Synergos MLOps":
            mlops_port = right_column.number_input(
                label="MLOps Port:", 
                value=11000
            )
            collab_task.configure_mlops(host=host, port=mlops_port)

        elif component == "Synergos MQ":
            mq_port = right_column.number_input(
                label="MQ Port:", 
                value=12000
            )
            collab_task.configure_mq(host=host, port=mq_port)

        elif component == "Synergos UI":
            ui_port = right_column.number_input(
                label="UI Port:", 
                value=13000
            )
            collab_task.configure_ui(host=host, port=ui_port)

    ##################################
    # Step 3: Register collaboration #
    ##################################

    st.header("Step 3: Submit your collaboration entry")

    with st.form("collab_declaration"):

        collaboration_configurations = collab_task._compile_configurations()
        with st.echo():
            st.write(collaboration_configurations)

        is_correct = st.checkbox(
            label="Confirm if details submitted are correct", 
            value=False, 
            help=None
        )

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")

        if is_correct and submitted:
            st.write(collab_task.address)
            collab_task.create(collab_id=collab_id)








    def render_upload_mods(self) -> Dict[str, List[Dict[str, Any]]]:
        """ Renders interface facilitating major architectural declarations for 
            a specific experiment submitted in a Synergos network

        Args:
            data (dict): Information relevant to a registered experiment
        Returns:
            Agumented model (dict)
        """
        with st.beta_container():
            columns = st.beta_columns(2)

            with columns[0]:

                uploaded_file = st.file_uploader(
                    label="Upload your model architecture:",
                    type="json",
                    help="Provide a parsable JSON file documenting each layer of your desired model"    
                )

                if uploaded_file is not None:
                    bytes_data = uploaded_file.getvalue()
                    stringio = StringIO(bytes_data.decode("utf-8"))
                    architecture_string = stringio.read()
                    architecture = {'model': json.loads(architecture_string)}
                else:
                    architecture = {'model': {}}  
                
                is_previewed = st.checkbox(label="Preview architecture")

            with columns[1]:
                if is_previewed:
                    with st.echo(code_location='below'):
                        st.write(architecture)
        
            st.markdown("---")

        return architecture





    with st.form(f"{r_type}_confirmation_declaration_{r_action}"):
        
        left_column, right_column = st.beta_columns(2)

        with left_column:
            is_previewed = st.checkbox(
                label=f"Preview {r_type} entry",
                value=False,
                help=None 
            )

            is_correct = st.checkbox(
                label="Confirm if details declared are correct", 
                value=False, 
                help=None
            )
            st.write(is_correct)

            if use_warnings:
                is_finalized = st.radio(
                    label="Are you sure? This action is not reversible!", 
                    index=1,
                    options=['Yes', 'No']
                )
                is_correct = is_correct and (is_finalized == 'Yes') 

            # Every form must have a submit button.
            is_submitted = st.form_submit_button("Submit")

        with right_column:
            st.write(is_previewed)
            if is_previewed:
                with st.echo(code_location="below"):
                    st.write(data)

    return is_correct and is_submitted





        with st.form(f"{r_type}_confirmation_declaration_{r_action}"):
        
        with st.echo():
            st.write(data)

        is_correct = st.checkbox(
            label="Confirm if details declared are correct", 
            value=False, 
            help=None
        )
        st.write(is_correct)
        if use_warnings:
            is_finalized = st.radio(
                label="Are you sure? This action is not reversible!", 
                index=1,
                options=['Yes', 'No']
            )
            is_correct = is_correct and (is_finalized == 'Yes') 

        # Every form must have a submit button.
        is_submitted = st.form_submit_button("Submit")

    return is_correct and is_submitted






def render_orchestrator_inputs() -> Union[Driver, None]:
    """ Renders input form for collecting orchestrator-related connection
        metadata, and assembles a Synergos Driver object for subsequent use.

    Returns:
        Connected Synergos Driver (Driver)
    """
    basic_input_container = st.sidebar.beta_container()
    left_column, right_column = basic_input_container.beta_columns(2)

    st.sidebar.title("GRID")
    orchestrator_host = st.sidebar.text_input(
        label="Orchestrator IP:",
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = st.sidebar.number_input(
        label="Orchestrator Port:",
        value=5000,
        help="Declare the access port of your selected orchestrator."
    )

    if orchestrator_host and orchestrator_port:
        driver = Driver(host=orchestrator_host, port=orchestrator_port)
    else:
        driver = None    # Ensures rendering of unpopulated widgets

    return driver











#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import streamlit as st

# Custom
from synergos import Driver
from synui.renderer import CollaborationRenderer
from synui.utils import (
    render_orchestrator_inputs,
    render_confirmation_form,
    render_collaborations,
    render_projects,
    render_experiments,
    render_runs,
    render_registrations
)

##################
# Configurations #
##################

SUPPORTED_ACTIONS = [
    "Create new collaboration(s)",
    "Browse existing collaboration(s)",
    "Update existing collaboration(s)",
    "Remove existing collaboration(s)"
]

DEFAULT_DEPLOYMENTS = {
    'Basic': [],
    'Monitored SME': [
        "Synergos Logger",
        "Synergos Meter",
        "Synergos MLOps",
        "Synergos UI"
    ],
    'SynCluster': [
        "Synergos Catalogue",
        "Synergos Logger",
        "Synergos Meter",
        "Synergos MLOps",
        "Synergos MQ",
        "Synergos UI"
    ]
}

R_TYPE = "collaboration"

collab_renderer = CollaborationRenderer()

###########
# Helpers #
###########


#########################################################
# Collaboration UI Option - Create new Collaboration(s) #
#########################################################

def create_collaborations():
    """ Main function that governs the creation of collaborations within a
        specified Synergos network
    """
    st.title("Orchestrator - Create New Collaboration(s)")

    ########################
    # Step 0: Introduction #
    ########################

    basic_input_container = st.beta_container()
    left_column, mid_column, right_column = basic_input_container.beta_columns(3)

    collab_id = left_column.text_input(
        label="Collaboration ID:",
        help="Declare the name of your new collaboration."
    )

    synergos_variant = mid_column.selectbox(
        label="Variant:",
        options=list(DEFAULT_DEPLOYMENTS.keys()),
        help="Declare which variant of Synergos you deployed for this collaboration."
    )

    deployment_mode = right_column.selectbox(
        label="Mode:",
        options=["local", "distributed"],
        help="""Declare which setting was Synergos deployed in. Selecting 
        'local' indicates that all components have been deployed onto the same 
        server. Conversely, selecting 'distributed' indicates a more complex
        network deployed."""
    )

    default_host = "localhost" if deployment_mode == 'local' else ""

    ##############################################################
    # Step 1: Connect Synergos Driver to a deployed orchestrator #
    ############################################################## 

    st.header("Step 1: Connect to your Orchestrator")
    driver_input_container = st.beta_container()
    left_column, right_column = driver_input_container.beta_columns(2)

    orchestrator_options = ["TTP" if synergos_variant != "SynCluster" else "Director"]
    orchestrator_deployed = left_column.selectbox(
        label="Orchestrator Type", 
        options=orchestrator_options,
        help="Orchestrator type will be dynamically inferred given your specified variant."
    )
    orchestrator_host = right_column.text_input(
        label="Orchestrator IP:",
        value=default_host,
        help="Declare the server IP of your selected orchestrator."
    )
    orchestrator_port = right_column.number_input(
        label="Orchestrator Port:",
        value=5000,
        help="Declare the access port of your selected orchestrator."
    )
    driver = Driver(host=orchestrator_host, port=orchestrator_port)

    ###########################################
    # Step 2: Declare all deployed components #
    ########################################### 

    st.header("Step 2: Declare all components of your Synergos Network")

    optional_components_deployed = st.multiselect(
        label="Supplementary components deployed for collaboration:", 
        options=[
            "Synergos Catalogue",
            "Synergos Logger",
            "Synergos Meter",
            "Synergos MLOps",
            "Synergos MQ",
            "Synergos UI"
        ], 
        default=DEFAULT_DEPLOYMENTS[synergos_variant],
        help="Declare which Addons were deployed alongside the core components."
    )

    collab_task = driver.collaborations
    for idx, component in enumerate(optional_components_deployed, start=1):

        st.markdown(f"{idx}. Register specs for {component}:")
        
        if component == "Synergos Catalogue":
            catalogue_info = collab_renderer.render_catalogue_metadata()
            collab_task.configure_catalogue(
                host=catalogue_info['catalogue_host'], 
                port=catalogue_info['catalogue_port']
            )

        elif component == "Synergos Logger":
            logger_info = collab_renderer.render_logger_metadata()
            logger_ports = logger_info['logger_ports']
            collab_task.configure_logger(
                host=logger_info['logger_host'], 
                sysmetrics_port=logger_ports['sysmetrics'],
                director_port=logger_ports['director'],
                ttp_port=logger_ports['ttp'],
                worker_port=logger_ports['worker']
            )

        elif component == "Synergos Meter":
            meter_info = collab_renderer.render_meter_metadata()
            collab_task.configure_meter(
                host=meter_info['meter_host'], 
                port=meter_info['meter_port']
            )

        elif component == "Synergos MLOps":
            mlops_info = collab_renderer.render_mlops_metadata()
            collab_task.configure_mlops(
                host=mlops_info['mlops_host'], 
                port=mlops_info['mlops_port']
            )

        elif component == "Synergos MQ":
            mq_info = collab_renderer.render_mq_metadata()
            collab_task.configure_mq(
                host=mq_info['mq_host'], 
                port=mq_info['mq_port']
            )

        elif component == "Synergos UI":
            ui_info = collab_renderer.render_ui_metadata()
            collab_task.configure_ui(
                host=ui_info['ui_host'], 
                port=ui_info['ui_port']
            )

    ##################################
    # Step 3: Register collaboration #
    ##################################

    st.header("Step 3: Submit your collaboration entry")
    collaboration_configurations = collab_task._compile_configurations()
    is_confirmed = render_confirmation_form(
        data=collaboration_configurations,
        r_type=R_TYPE,
        r_action="creation",
        use_warnings=False    
    )
    if is_confirmed:
        collab_task.create(collab_id=collab_id)



##############################################################
# Collaboration UI Option - Browse Existing Collaboration(s) #
##############################################################

def browse_collaborations():
    """ Main function that governs the browsing of collaborations within a
        specified Synergos network
    """
    st.title("Orchestrator - Browse Existing Collaboration(s)")

    ########################
    # Step 0: Introduction #
    ########################


    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    st.header("Step 1: Connect to an Orchestrator")
    collab_driver = render_orchestrator_inputs()

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 2: Select your collaboration of interest")
    selected_collab_id, _ = render_collaborations(driver=collab_driver)

    ########################################################################
    # Step 3: Pull associations & relationships of specified collaboration #
    ########################################################################

    st.header("Step 3: Explore Relationships & Associations")
    selected_project_id, _ = render_projects(
        driver=collab_driver, 
        collab_id=selected_collab_id
    )

    selected_expt_id, _ = render_experiments(
        driver=collab_driver, 
        collab_id=selected_collab_id,
        project_id=selected_project_id
    )
    
    render_runs(
        driver=collab_driver, 
        collab_id=selected_collab_id,
        project_id=selected_project_id,
        expt_id=selected_expt_id
    )

    ###########################################################
    # Step 4: Browse registrations of specified collaboration #
    ###########################################################

    st.header("Step 4: Browse Participant Registry")
    render_registrations(
        driver=collab_driver,
        collab_id=selected_collab_id,
        project_id=selected_project_id
    )



##############################################################
# Collaboration UI Option - Update existing collaboration(s) #
##############################################################

def update_collaborations():
    """ Main function that governs the updating of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title("Orchestrator - Update existing collaboration(s)")

    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    st.header("Step 1: Connect to an Orchestrator")
    collab_driver = render_orchestrator_inputs()

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 2: Modify your collaboration of interest")
    if collab_driver:
        collab_data = collab_driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in collab_data]
    else:
        collab_ids = []

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="""Select a collaboration to peruse."""
        )

        if collab_driver:
            selected_collab_data = collab_driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
            updated_collab = collab_renderer.display(selected_collab_data)
                
    ##################################
    # Step 3: Register collaboration #
    ##################################

    st.header("Step 3: Submit your collaboration entry")
    is_confirmed = render_confirmation_form(
        data=updated_collab,
        r_type=R_TYPE,
        r_action="update",
        use_warnings=False    
    )
    if is_confirmed:
        collab_driver.collaborations.update(
            collab_id=selected_collab_id, 
            **updated_collab
        )



##############################################################
# Collaboration UI Option - Remove existing collaboration(s) #
##############################################################

def remove_collaborations():
    """ Main function that governs the deletion of metadata in a collaborations 
        within a specified Synergos network
    """
    st.title("Orchestrator - Remove existing collaboration(s)")

    ##################################################
    # Step 1: Connect to your specified orchestrator #
    ##################################################

    st.header("Step 1: Connect to an Orchestrator")
    collab_driver = render_orchestrator_inputs()

    ######################################################################
    # Step 2: Pull collaboration information from specified orchestrator #
    ######################################################################

    st.header("Step 2: Target your collaboration of interest")
    if collab_driver:
        collab_data = collab_driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in collab_data]
    else:
        collab_ids = []

    with st.beta_container():

        selected_collab_id = st.selectbox(
            label="Collaboration ID:", 
            options=collab_ids,
            help="""Select a collaboration to peruse."""
        )

        if collab_driver:
            selected_collab_data = collab_driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
            updated_collab = collab_renderer.display(selected_collab_data)
                
    ################################
    # Step 3: Remove collaboration #
    ################################

    st.header("Step 3: Submit removal request for collaboration ")
    is_confirmed = render_confirmation_form(
        data=updated_collab,
        r_type=R_TYPE,
        r_action="removal",
        use_warnings=False    
    )
    if is_confirmed:
        collab_driver.collaborations.delete(collab_id=selected_collab_id)
        st.echo(f"Collaboration '{selected_collab_id}' has been deleted.")
            


######################################
# Collaboration UI - Page Formatting #
######################################

def app():
    """ Main app orchestrating collaboration management procedures """
    option = st.sidebar.selectbox(
        label='Select action to perform:', 
        options=SUPPORTED_ACTIONS,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    driver = render_orchestrator_inputs()

    if option == "Create new collaboration(s)":
        create_collaborations(driver)

    elif option == "Browse existing collaboration(s)":
        browse_collaborations(driver)

    elif option == "Update existing collaboration(s)":
        update_collaborations(driver)

    elif option == "Remove existing collaboration(s)":
        remove_collaborations(driver) 












hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""







            # Every form must have a submit button.
            is_correct = False
            is_submitted = st.form_submit_button("Submit")

            left_column, right_column = st.beta_columns(2)

            with left_column:
                is_previewed = st.checkbox(
                    label=f"Preview {r_type} entry",
                    value=False
                )

                is_correct = st.checkbox(
                    label="Confirm if details declared are correct", 
                    value=False, 
                    help=None
                )
                if is_correct and use_warnings:
                    is_finalized = st.selectbox(
                        label="Are you sure? This action is not reversible!", 
                        index=1,
                        options=['Yes', 'No']
                    )
                    is_correct = is_correct and (is_finalized == 'Yes') 

                is_submitted = st.button(label="Submit")

            with right_column:
                if is_previewed:
                    with st.echo(code_location="below"):
                        st.write(data)












def render_upstream_hierarchy(r_type: str, driver: Driver):
    """
    """
    SUPPORTED_RECORDS = ["collaboration", "project", "experiment", "run"]

    with st.sidebar.beta_container():

        st.header("FILTERS")
        combination_key = {}

        if r_type in SUPPORTED_RECORDS[1:]:
            selected_collab_id, _ = render_collaborations(
                driver=driver,
                show_details=False
            )
            combination_key['collab_id'] = selected_collab_id

            if r_type in SUPPORTED_RECORDS[2:]:
                selected_project_id, _ = render_projects(
                    driver=driver,
                    collab_id=selected_collab_id,
                    show_details=False
                )
                combination_key['project_id'] = selected_project_id

                if r_type in SUPPORTED_RECORDS[3:]:
                    selected_expt_id, _ = render_experiments(
                        driver=driver,
                        collab_id=selected_collab_id,
                        project_id=selected_project_id,
                        show_details=False
                    )
                    combination_key['expt_id'] = selected_expt_id

    return combination_key



def render_upstream_hierarchy(r_type: str, driver: Driver):
    """
    """
    SUPPORTED_RECORDS = ["collaboration", "project", "experiment", "run"]

    with st.sidebar.beta_container():

        st.sidebar.header("FILTERS")
        combination_key = {}

        if r_type in SUPPORTED_RECORDS[1:]:
            if driver:
                collab_data = driver.collaborations.read_all().get('data', [])
                collab_ids = [collab['key']['collab_id'] for collab in collab_data]
            else:
                collab_ids = []

            selected_collab_id = st.sidebar.selectbox(
                label="Collaboration ID:", 
                options=collab_ids,
                help="""Select a collaboration to peruse."""
            )
            combination_key['collab_id'] = selected_collab_id

            if r_type in SUPPORTED_RECORDS[2:]:
                if driver and selected_collab_id:
                    project_data = driver.projects.read_all(selected_collab_id).get('data', [])
                    project_ids = [proj['key']['project_id'] for proj in project_data]
                else:
                    project_ids = []

                selected_project_id = st.sidebar.selectbox(
                    label="Project ID:", 
                    options=project_ids,
                    help="""Select a project to peruse."""
                )
                combination_key['project_id'] = selected_project_id

                if r_type in SUPPORTED_RECORDS[3:]:
                    if driver and selected_collab_id and selected_project_id:
                        expt_data = driver.experiments.read_all(
                            collab_id=selected_collab_id, 
                            project_id=selected_project_id
                        ).get('data', [])
                        expt_ids = [expt['key']['expt_id'] for expt in expt_data]
                    else:
                        expt_ids = []

                    selected_expt_id = st.sidebar.selectbox(
                        label="Experiment ID:", 
                        options=expt_ids,
                        help="""Select an experiment to peruse."""
                    )
                    combination_key['expt_id'] = selected_expt_id

    return combination_key 









import pptree






                    data_tree = pptree.Node(f"{dataset_type} Structure")

                    node_mappings = {}
                    prev_node = data_tree
                    for tags in data_meta_tags:
                        for node_name in tags:

                            if node_name in node_mappings:
                                curr_node = node_mappings.get(node_name)
                            else:
                                curr_node = pptree.Node(node_name, parent=prev_node)
                            
                            node_mappings[node_name] = curr_node
                            prev_node = curr_node

                with st.echo():
                    st.write(str(data_tree)) 





                    node_mappings = {}
                    for tags in data_meta_tags:

                        st.write(tags)
                        prev_node = data_tree
                        for node_name in tags:
                            
                            if node_name in node_mappings:
                                curr_node = node_mappings.get(node_name)
                            else:
                                curr_node = pydot.Node(
                                    node_name, 
                                    label=node_name,
                                    shape='circle'
                                )
                                data_tree.add_node(curr_node)

                            if not data_tree.get_edge(
                                prev_node.get_name(),
                                curr_node.get_name(), 
                            ):
                                my_edge = pydot.Edge(
                                    prev_node.get_name(), 
                                    curr_node.get_name(), 
                                    color='blue'
                                )
                                data_tree.add_edge(my_edge)
                                node_mappings[node_name] = curr_node
                                prev_node = curr_node


                    tree_png = data_tree.create_png()
                    st.image(tree_png)




            st.write(tags)

            prev_idx = 0
            curr_idx = 0
            while curr_idx < len(tags):

                prev_token = tags[prev_idx]
                curr_token = tags[curr_idx]
                prev_keypoint = tag_keypoints.get(prev_token, [])

                prev_keypoint.append(curr_token)
                tag_keypoints.update({prev_token: prev_keypoint})

                if prev_idx == curr_idx:
                    curr_idx += 1
                else:
                    prev_idx += 1
                    curr_idx += 1



    def __parse_to_tree(self, meta: str, data_tags: List[List[str]]):
        """
        """
        if data_tags:
            
            data_tree = pydot.Dot(
                f"{meta.upper()} Dataset Structure", 
                # graph_type='graph', 
                rankdir="LR",
                fillcolor="white",
                bgcolor="#0E1117"
            )
            data_tree.set_node_defaults(
                color='white',
                style='filled',
                shape='box',
                fontname='Courier',
                fontsize='10'
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

            # Construct all edges between valid nodes
            # for tags in data_tags:

            #     tag_colour = generate_hex_colour()
            #     prev_node_name = data_tree.get_name()
            #     for node_name in tags:

            #         if not data_tree.get_edge(prev_node_name, node_name):
            #             node_edge = pydot.Edge(
            #                 prev_node_name, 
            #                 node_name, 
            #                 color=tag_colour
            #             )
            #             data_tree.add_edge(node_edge)

            #         prev_node_name = node_name

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
                tree_png = data_tree.create_png()
                st.image(
                    tree_png, 
                    caption=f"{meta.upper()} Dataset Hierarchy",
                    use_column_width='always'
                )
        



    def __parse_to_tags(self, meta):
        """
        """
        options_container = st.empty()
        path_input_container = st.empty()
      
        src_path = path_input_container.text_input(label="Data source:")
        is_added = st.button(label="Add")  
        is_resetted = st.button("Reset") 

        if src_path and is_added:
            self._options.append(src_path)
        
        selected_paths = options_container.multiselect(
            label="dadaa", 
            options=self._options, 
            default=self._options,
            key=f"{meta}_options"
        )
        self._options = selected_paths

        selected_tags = [path.split('/') for path in selected_paths]
        st.write(selected_tags)
        

        # self.options = selected_paths




def render_participant_registrations(
    driver: Driver = None, 
    participant_id: str = None,
    collab_id: str = None,
    project_id: str = None
):
    """ Renders out retrieved registration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        collab_id (str): ID of selected collaboration to be rendered
        project_id (str): ID of selected project to be rendered
    """
    if participant_id:
        participant_data = driver.participants.read(participant_id).get('data', {})
    else:
        participant_data = {}

    participant_relations = participant_data.get('relations', {})
    participant_registrations = participant_relations.get('Registration', [])
    
    registry_mapping = {}
    for registration in participant_registrations:
        curr_collab_id = registration.get('key', {}).get('collab_id')
        curr_collab = registry_mapping.get(curr_collab_id, {})
        curr_project_id = registration.get('key', {}).get('project_id') 
        curr_collab[curr_project_id] = registration   
        registry_mapping[curr_collab_id] = curr_collab     

    registered_collab_ids = list(registry_mapping.keys())
    selected_collab_id = st.selectbox(
        label="Collaboration ID:", 
        options=registered_collab_ids,
        help="""Select a collaboration to view."""
    )

    # relevant_project_ids = list(registry_mapping.get(selected_collab_id, {}).keys())
    # selected_project_id = st.selectbox(
    #     label="Project ID:", 
    #     options=relevant_project_ids,
    #     help="""Select a collaboration to view."""
    # )
    selected_project_id, _ = render_projects(
        driver=driver,
        collab_id=selected_collab_id
    )

    relevant_entry = registry_mapping.get(selected_collab_id, {}).get(selected_project_id, {})
    
    with st.beta_expander("Registration Details"):
        reg_renderer.display(data=relevant_entry)

    return selected_collab_id, {}






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

        tag_details = {}
        for dataset_type in dataset_types:
            with st.beta_container():
                columns = st.beta_columns((1, 2))

                with columns[0]:
                    data_meta_tags = self.__parse_to_tags(meta=dataset_type)

                with columns[1]:
                    self.__parse_to_tree(
                        meta=dataset_type, 
                        data_tags=data_meta_tags
                    )

                tag_details[dataset_type] = data_meta_tags

                st.markdown("---")
                
        return {
            'train': updated_train_tags,
            'evaluate': updated_eval_tags,
            'predict': updated_predict_tags
        }



    def __parse_to_tags(self, meta: str, tag_string: str) -> List[List[str]]:
        """ Acquires and convert declared paths to data sources into data tags 

        Args:
            meta (str): Type of data tags processed (i.e. 'train'/'evaluate'/'predict')
        Returns:
            Meta-specific Data tags (list)
        """           
        data_meta_string = st.text_area(
            label=f"Declare all {meta.upper()} tags options:", 
            height=300,
            key=meta
        ).replace('\'', '"')

        data_meta_paths = data_meta_string.splitlines()

        options_container = st.empty()
        self._options = options_container.multiselect(
            label=f"{meta.upper()} Data Sources:", 
            options=data_meta_paths, 
            default=data_meta_paths,
            key=f"{meta}_options"
        )

        data_meta_tokens = [
            Path(path_str).parts[1:] 
            for path_str in self._options
        ]
        return data_meta_tokens




    with st.beta_container():
        left_column, mid_column, right_column = st.beta_columns(3)

        with left_column:
            with st.beta_expander("Registration Details"):
                reg_renderer.display(selected_registry)

        with mid_column:
            with st.beta_expander("Tag Details"):
                tags = selected_registry.get('relations', {}).get('Tag', [])
                tag_details = tags.pop() if tags else {}
                tag_renderer.display(tag_details, is_stacked=True)

        with right_column:
            with st.beta_expander("Alignment Details"):
                alignments = selected_registry.get('relations', {}).get('Alignment', [])
                alignment_details = alignments.pop() if alignments else {}
                align_renderer.display(alignment_details)




    # def render_tag_metadata(
    #     self, 
    #     data: Dict[str, Any] = {},
    #     is_stacked: bool = False
    # ) -> Dict[str, List[List[str]]]:
    #     """ Renders a form capturing dataset tags registered for use 
    #         under by a participant in a deployed Synergos network, given its 
    #         prerequisite information, as well as any updates to their values.

    #     Args:
    #         data (dict): Information relevant to a tag entry
    #     Returns:
    #         Updated data tags (dict)
    #     """     
    #     TAG_KEYS = ["train", "evaluate", "predict"]

    #     for key, value in data.items():

    #         if key in TAG_KEYS:

    #             with st.beta_container():
    #                 columns = st.beta_columns((1, 2))

    #                 with columns[0]:
    #                     data_meta_string = st.text_area(
    #                         label=f"Declare all {dataset_type.upper()} tags options:", 
    #                         height=300,
    #                         key=dataset_type
    #                     ).replace('\'', '"')
    #                     data_meta_tags = self.__parse_to_tags(
    #                         meta=dataset_type,
    #                         tag_string=data_meta_string
    #                     )

    #                 with columns[1]:
    #                     self.__parse_to_tree(
    #                         meta=dataset_type, 
    #                         data_tags=data_meta_tags
    #                     )

    #                 tag_paths = [
    #                     Path(*[os.sep, *tokens]).as_posix() 
    #                     for tokens in value
    #                 ]
    #                 updated_meta_string = columns[0].text_area(
    #                     label=f"{key} Data Tags", 
    #                     value="\n".join(tag_paths),
    #                     height=200
    #                 )
    #                 updated_meta_tags = self.__parse_to_tags(
    #                     meta=key,
    #                     tag_string=updated_meta_string
    #                 )

    #                 self.__parse_to_tree(
    #                     meta=key, 
    #                     data_tags=updated_meta_tags
    #                 )

    #                 st.markdown("---")


        # tag_details = {}
        # for dataset_type in dataset_types:
        #     with st.beta_container():
        #         columns = st.beta_columns((1, 2))

        #         with columns[0]:
        #             data_meta_tags = self.__parse_to_tags(meta=dataset_type)

        #         with columns[1]:
        #             self.__parse_to_tree(
        #                 meta=dataset_type, 
        #                 data_tags=data_meta_tags
        #             )

        #         tag_details[dataset_type] = data_meta_tags

        #         st.markdown("---")

        # return {
        #     'train': updated_train_tags,
        #     'evaluate': updated_eval_tags,
        #     'predict': updated_predict_tags
        # }




    def render_registration_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, Union[int, str, bool]]]:
        """ Renders a form capturing existing nodes registered for use 
            under by a participant in a deployed Synergos network, given its 
            prerequisite information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Updated registration (dict)
        """       
        node_details = {
            reg_key: reg_value
            for reg_key, reg_value in data.items()
            if "node_" in reg_key 
        }

        updated_nodes = {}
        for node_idx, node_info in sorted(
            node_details.items(), 
            key=lambda x: x[0]
        ):
            host = node_info.get('host', "")
            rpc_port = node_info.get('f_port', "")
            syft_port = node_info.get('port', "")
            log_msgs = node_info.get('log_msgs', False)
            verbose = node_info.get("verbose", False)

            node_name = " ".join(node_idx.capitalize().split('_'))
            
            with st.beta_container():

                st.header(node_name)

                updated_host = st.text_input(
                    label="IP Address:", 
                    value=host, 
                    key=uuid.uuid4()
                )
                updated_rpc_port = st.text_input(
                    label="RPC Port:", 
                    value=rpc_port, 
                    key=uuid.uuid4()
                )
                updated_syft_port = st.text_input(
                    label="Syft Port:", 
                    value=syft_port, 
                    key=uuid.uuid4()
                )

                log_msgs = st.checkbox(
                    label=f"{node_name}: Display logs", 
                    value=log_msgs
                )

                if log_msgs:
                    verbose = st.checkbox(
                        label=f"{node_name}: Use verbose view", 
                        value=verbose
                    )

            updated_nodes[node_idx] = {
                'host': updated_host,
                'f_port': updated_rpc_port,
                'port': updated_syft_port,
                'log_msgs': log_msgs,
                'verbose': verbose
            }

        return updated_nodes



    def render_registration_metadata(
        self, 
        data: Dict[str, Any] = {}
    ) -> Dict[str, Dict[str, Union[int, str, bool]]]:
        """ Renders a form capturing existing nodes registered for use 
            under by a participant in a deployed Synergos network, given its 
            prerequisite information, as well as any updates to their values.

        Args:
            data (dict): Information relevant to a registration entry
        Returns:
            Updated registration (dict)
        """       
        node_details = {
            reg_key: reg_value
            for reg_key, reg_value in data.items()
            if "node_" in reg_key 
        }

        updated_nodes = {}
        for node_idx, node_info in sorted(
            node_details.items(), 
            key=lambda x: x[0]
        ):
            host = node_info.get('host', "")
            rpc_port = node_info.get('f_port', "")
            syft_port = node_info.get('port', "")
            log_msgs = node_info.get('log_msgs', False)
            verbose = node_info.get("verbose", False)

            node_name = " ".join(node_idx.capitalize().split('_'))
            
            with st.beta_container():

                st.header(node_name)

                updated_host = st.text_input(
                    label="IP Address:", 
                    value=host, 
                    key=uuid.uuid4()
                )
                updated_rpc_port = st.text_input(
                    label="RPC Port:", 
                    value=rpc_port, 
                    key=uuid.uuid4()
                )
                updated_syft_port = st.text_input(
                    label="Syft Port:", 
                    value=syft_port, 
                    key=uuid.uuid4()
                )

                log_msgs = st.checkbox(
                    label=f"{node_name}: Display logs", 
                    value=log_msgs
                )

                if log_msgs:
                    verbose = st.checkbox(
                        label=f"{node_name}: Use verbose view", 
                        value=verbose
                    )

            updated_nodes[node_idx] = {
                'host': updated_host,
                'f_port': updated_rpc_port,
                'port': updated_syft_port,
                'log_msgs': log_msgs,
                'verbose': verbose
            }

        return updated_nodes

['a', 'b', 'c', 'd']
['a', 'b', 'c', 'e']
['a', 'b', 'f', 'g']
['a', 'b', 'f', 'h']
['a', 'b', 'f', 'd']



/a/b/c/d
/a/b/c/e
/a/b/c/f
/a/b/g/h
/a/b/g/i
/a/b/j/k