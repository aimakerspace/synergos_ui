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
from synui.ui_inference import app as infer_app
from synui.landing import app as landing_app
from synui.submission import app as submit_app
from synui.analysis import app as analysis_app
from synui.utils import MultiApp, render_svg

##################
# Configurations #
##################

FAVICON_PATH = os.path.join(ASSETS_DIR, "images", "Synergos-Favicon.ico")

PLACEHOLDER_OPTION = "Select an option"

SUPPORTED_ROLES = [PLACEHOLDER_OPTION, "Orchestrator", "Participant"]

SUPPORTED_DEFAULT_PROCESSES = {
    PLACEHOLDER_OPTION: landing_app, 
    # "Construct a deployment script": None
}

SUPPORTED_ORCHESTRATOR_PROCESSES = {
    **SUPPORTED_DEFAULT_PROCESSES,
    "Manage collaboration(s)": collab_app,
    "Manage project(s)": project_app,
    "Manage experiment(s)": expt_app,
    "Manage run(s)": run_app,
    "Submit federated job(s)": submit_app,
    # "Analyse federated job(s)": analysis_app,
    # "Optimize a model": None
}

SUPPORTED_PARTICIPANT_PROCESSES = {
    **SUPPORTED_DEFAULT_PROCESSES,
    "Manage your profile": participant_app,
    "Manage your registrations": reg_app,
    "Submit inference(s)": infer_app
}

st.set_page_config(
    page_title="Synergos UI", 
    page_icon=FAVICON_PATH,
    layout="wide"
)

######################################
# Main Synergos UI - Page formatting #
######################################

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """ Heart of the streamlit App """
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
                federated cycle? Or perhaps a participant looking to enroll in \
                an existing collaboration?"
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





###########
# Scripts #
###########

if __name__ == "__main__":
    main()












    <!-- <div class="dropdown">
        <button class="dropbtn">Dropdown</button>
        <div class="dropdown-content">
            <a href="#">Link 1</a>
            <a href="#">Link 2</a>
            <a href="#">Link 3</a>
        </div>
    </div>

    <ul>
        <li>
            <a class="navbar-brand" href="/">
                <div class="logo-image">
                    <img src="/static/images/synergos_logo.png" class="img-fluid">
                </div>
            </a>
        </li>
        <li>
            <a href="#" onclick="setURL('http://localhost:8501/?p=analysis')">Analysis</a>
        </li>
        <li>
            <a href="#" onclick="setURL('http://localhost:8501/?p=results')">Results</a>
        </li>
        <li>
            <a href="#" onclick="setURL('http://localhost:8501/?p=examples')">Examples</a>
        </li>
    </ul> -->



/* #streamlit-content {
    display       : flex;
    flex-direction: row;
    width         : 100%;
    height        : 100%;
    position      : fixed;
    border        : none;
    left          : 60px;
    right         : 0;
    z-index       : 0;
    transition    : left .1s linear;
    overflow      : hidden;
}


.main-menu:hover+#streamlit-content {
    left: 250px;
} */




#999


        <!-- AISG Facade Font Dependency -->
        <link href='https://fonts.googleapis.com/css?family=Josefin Sans' rel='stylesheet'>

        <div class="col s12 m7">
            <div class="card horizontal">
            <div class="card-image">
                <img src="https://i.ibb.co/fY1dtQQ/cat.jpg ">
            </div>
            <div class="card-stacked">
                <div class="card-content">
                <p>I am a very simple card. I am good at containing small bits of information.</p>
                </div>
                <div class="card-action">
                <a href="#">This is a link</a>
                </div>
            </div>
            </div>
        </div>


        <!-- Bootstrap CSS CDN -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css"
            integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorigin="anonymous">


        <div class="card-deck">
            <div class="card">
                <div class="card-body">
                <h5 class="card-title">Orchestrator</h5>
                <p class="card-text">This is a longer card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
                </div>
            </div>
            <div class="card">
                <img src="..." class="card-img-top" alt="...">
                <div class="card-body">
                <h5 class="card-title">Participants</h5>
                <p class="card-text">This card has supporting text below as a natural lead-in to additional content.</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                </div>
            </div>
        </div>


        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
            integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
            crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns"
            crossorigin="anonymous"></script>






<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/home">Home</a></li>
        <li class="breadcrumb-item active" aria-current="page"><a href="/orchestrator">Orchestrator</a></li>
    </ol>
</nav>








    # resize_iframes_style = """
    # <style>
    #     iframe {
    #         resize: both;
    #         overflow: auto;
    #     }
    # </style>
    # """#011839
    # st.markdown(resize_iframes_style, unsafe_allow_html=True) 







def main():
    """ Heart of the streamlit App """
    st.set_page_config(layout="wide")

    production_styles = read_production_css()
    st.markdown(production_styles, unsafe_allow_html=True) 

    with st.sidebar.beta_container():

        st.header("OPTIONS")

        role = st.selectbox(
            label='What is your role?', 
            options=SUPPORTED_ROLES,
            help="State your role for your current visit to Synergos. Are you a \
                trusted third party (i.e. TTP) looking to orchestrate your own \
                federated cycle? Or perhaps a participant looking to enroll in \
                an existing collaboration?"
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








PLACEHOLDER_OPTION = "Select an option"

SUPPORTED_ROLES = [PLACEHOLDER_OPTION, "Orchestrator", "Participant"]

SUPPORTED_DEFAULT_PROCESSES = {
    PLACEHOLDER_OPTION: landing_app, 
    # "Construct a deployment script": None
}

SUPPORTED_ORCHESTRATOR_PROCESSES = {
    **SUPPORTED_DEFAULT_PROCESSES,
    "Manage collaboration(s)": collab_app,
    "Manage project(s)": project_app,
    "Manage experiment(s)": expt_app,
    "Manage run(s)": run_app,
    "Submit federated job(s)": submit_app,
    # "Analyse federated job(s)": analysis_app,
    # "Optimize a model": None
}

SUPPORTED_PARTICIPANT_PROCESSES = {
    **SUPPORTED_DEFAULT_PROCESSES,
    "Manage your profile": participant_app,
    "Manage your registrations": reg_app,
    "Submit inference(s)": infer_app
}





















def app():
    """
    """
    st.title("Welcome to Synergos Portal")

    #####################
    # Dashboard Section #
    #####################

    st.header("Dashboards")

    orchestrator_b64_tag = render_png(
        ORCHESTRATOR_ICON_PATH,
        None,
        False, 
        *['class="card-img-top"', 'height="30px"', 'width="auto"']
    )

    components.html(
        f"""
        <!-- Bootstrap CSS CDN -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css"
            integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorigin="anonymous">


        <div class="card-deck">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Orchestrator</h5>
                    <p class="card-text">A trusted third party (i.e. TTP) looking to orchestrate your own federated cycle</p>
                    <p class="card-text"><small class="text-muted">Proceed</small></p>
                </div>
            </div>
            <div class="card">
                <img src="..." class="card-img-top" alt="...">
                <div class="card-body">
                <h5 class="card-title">Participants</h5>
                <p class="card-text">This card has supporting text below as a natural lead-in to additional content.</p>
                <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
                </div>
            </div>
        </div>


        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
            integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
            crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns"
            crossorigin="anonymous"></script>
        """,
        height=200
    )

    #####################
    # Resources Section #
    #####################

    st.header("Resources")

    components.html(
        f"""
        <!-- Bootstrap CSS CDN -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css"
            integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorigin="anonymous">

        <div class="card-columns">
        <div class="card">
            <img src="..." class="card-img-top" alt="...">
            <div class="card-body">
            <h5 class="card-title">Card title that wraps to a new line</h5>
            <p class="card-text">This is a longer card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
            </div>
        </div>
        <div class="card p-3">
            <blockquote class="blockquote mb-0 card-body">
            <p>A well-known quote, contained in a blockquote element.</p>
            <footer class="blockquote-footer">
                <small class="text-muted">
                Someone famous in <cite title="Source Title">Source Title</cite>
                </small>
            </footer>
            </blockquote>
        </div>
        <div class="card">
            <img src="..." class="card-img-top" alt="...">
            <div class="card-body">
            <h5 class="card-title">Card title</h5>
            <p class="card-text">This card has supporting text below as a natural lead-in to additional content.</p>
            <p class="card-text"><small class="text-muted">Last updated 3 mins ago</small></p>
            </div>
        </div>
        <div class="card bg-primary text-white text-center p-3">
            <blockquote class="blockquote mb-0">
            <p>A well-known quote, contained in a blockquote element.</p>
            <footer class="blockquote-footer text-white">
                <small>
                Someone famous in <cite title="Source Title">Source Title</cite>
                </small>
            </footer>
            </blockquote>
        </div>
        </div>

        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
            integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
            crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns"
            crossorigin="anonymous"></script>
        """,
        height=300
    )








    multiapp = MultiApp()

    if requested_view == "collaborations":
        multiapp.add_app(title="Manage collaboration(s)", func=collab_app)
        # collab_app()

    elif requested_view == "projects":
        multiapp.add_app(title="Manage collaboration(s)", func=collab_app)

    elif requested_view == "experiments":
        multiapp.add_app(title="Manage collaboration(s)", func=collab_app)

    elif requested_view == "runs":
        multiapp.add_app(title="Manage collaboration(s)", func=collab_app)

    elif requested_view == "optimizations":
        multiapp.add_app(collab_app)

    elif requested_view == "analysis":
        multiapp.add_app(collab_app)

    elif requested_view == "profiles":
        multiapp.add_app(collab_app)  

    elif requested_view == "registrations":
        multiapp.add_app(collab_app)  

    elif requested_view == "":
        multiapp.add_app(collab_app)  

    multiapp.run() 









.main-menu li:hover>a,
nav.main-menu li.active>a,
.dropdown-menu>li>a:hover,
.dropdown-menu>li>a:focus,
.dropdown-menu>.active>a,
.dropdown-menu>.active>a:hover,
.dropdown-menu>.active>a:focus,
.no-touch .dashboard-page nav.dashboard-menu ul li:hover a,
.dashboard-page nav.dashboard-menu ul li.active a {
    color              : #ffffff;
    background-color: #d87f4d;
}

li.active {

}
 









@import url(//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css);
@import url(https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css);
@import url(https://fonts.googleapis.com/css?family=Titillium+Web:300);

.fa-2x {
    font-size: 2em;
}

.fa {
    position      : relative;
    display       : table-cell;
    width         : 60px;
    height        : 36px;
    text-align    : center;
    vertical-align: middle;
    font-size     : 25px;
}

.main-menu {
    background        : #000000;
    border-right      : 1px solid #ffffff;
    position          : absolute;
    top               : 76px;
    bottom            : 0;
    height            : auto;
    left              : 0;
    width             : 60px;
    overflow          : hidden;
    -webkit-transition: width .1s linear;
    transition        : width .1s linear;
    -webkit-transform : translateZ(0) scale(1, 1);
    z-index           : 1000;
}

.main-menu:hover,
nav.main-menu.expanded {
    width   : 250px;
    overflow: visible;
}

/* Formatting Synergos Logo & Animations */
.main-menu>div.menu-logo {
    display           : flex;
    justify-content   : center;
    margin-top        : 10px;
    margin-bottom     : 10px;
    -webkit-transition: all .1s linear;
    transition        : all .1s linear;
}

.menu-logo>img {
    width             : 50px;
    height            : 50px;
    object-fit        : contain;
    -webkit-transition: all .1s linear;
    transition        : all .1s linear;
    position          : fixed;
}

.menu-logo>h1.menu-logo-text {
    visibility: hidden;
}

.menu-logo-text {
    display: block;
}

.main-menu:hover>div.menu-logo {
    vertical-align: top;
    display       : inline-block;
    text-align    : center;
    margin-bottom : 100px;
}

.main-menu:hover>.menu-logo>img {
    width   : 250px;
    height  : 250px;
    position: relative;
}

.main-menu:hover>.menu-logo>h1.menu-logo-text {
    color      : #ffffff;
    font-family: arial;
    visibility : visible;
}


/* Formatting Synergos Side Menu & Animations */
.main-menu>ul {
    margin: 7px 0;
}

.main-menu li {
    position: relative;
    display : block;
    width   : 250px;
}

.main-menu li>a {
    position          : relative;
    display           : table;
    border-collapse   : collapse;
    border-spacing    : 0;
    color             : #ffffff;
    font-family       : arial;
    font-size         : 18px;
    text-decoration   : none;
    -webkit-transform : translateZ(0) scale(1, 1);
    -webkit-transition: all .1s linear;
    transition        : all .1s linear;

}

.main-menu .nav-icon {
    position      : relative;
    display       : table-cell;
    width         : 60px;
    height        : 36px;
    text-align    : center;
    vertical-align: middle;
    font-size     : 18px;
}

.main-menu .nav-text {
    position      : relative;
    display       : table-cell;
    vertical-align: middle;
    width         : 190px;
    font-family   : 'Titillium Web', sans-serif;
}

.main-menu>ul.helpline {
    position: absolute;
    left    : 0;
    bottom  : 0;
}

/* .no-touch .scrollable.hover {
    overflow-y: hidden;
}

.no-touch .scrollable.hover:hover {
    overflow-y: auto;
    overflow  : visible;
} */

a:hover,
a:focus {
    text-decoration: none;
}

nav {
    -webkit-user-select: none;
    -moz-user-select   : none;
    -ms-user-select    : none;
    -o-user-select     : none;
    user-select        : none;
}

nav ul,
nav li {
    outline    : 0;
    margin     : 0;
    padding    : 0;
    line-height: 60px;
}

nav.main-menu li.active>a {
    color           : #ffffff;
    background-color: #d87f4d;
}

nav.main-menu li:hover:not(.active)>a {
    color: #d87f4d;
}

.area {
    float     : left;
    background: #e2e2e2;
    width     : 100%;
    height    : 100%;
}

@font-face {
    font-family: 'Titillium Web';
    font-style : normal;
    font-weight: 300;
    src        : local('Titillium WebLight'), local('TitilliumWeb-Light'), url(http://themes.googleusercontent.com/static/fonts/titilliumweb/v2/anMUvcNT0H1YN4FII8wpr24bNCNEoFTpS2BTjF6FB5E.woff) format('woff');
}














nav.main-menu li:hover:not(.active)>a {
    background-color: #d87f4d;
}













/* .area {
    float     : left;
    background: #e2e2e2;
    width     : 100%;
    height    : 100%;
} */


















    <div class="row">
        <div class="col-md-5">
            <div class="card">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/collaboration.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Manage Collaborations</h5>
                            <p class="card-text">Deployment starts here!</p>
                            <p class="card-text">
                                <a href="/view/orchestrator/collaborations" class="custom-button">
                                    <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-5">
            <div class="card mb-3">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/project.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Manage Projects</h5>
                            <p class="card-text">Configure dataset variants here!</p>
                            <p class="card-text">
                                <small class="text-muted">
                                    <a href="/view/projects" class="custom-button">
                                        <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                    </a>
                                </small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-5">
            <div class="card">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/experiment.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Manage Experiments</h5>
                            <p class="card-text">Try out different model architectures here!</p>
                            <p class="card-text">
                                <a href="/view/experiments" class="custom-button">
                                    <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-5">
            <div class="card mb-3">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/run.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Manage Runs</h5>
                            <p class="card-text">Try out different hyperparameter sets here!</p>
                            <p class="card-text">
                                <small class="text-muted">
                                    <a href="/view/runs" class="custom-button">
                                        <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                    </a>
                                </small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-md-5">
            <div class="card">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/optimizer.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Optimize Performance</h5>
                            <p class="card-text">Tune your model(s) here!</p>
                            <p class="card-text">
                                <a href="/view/optimizations" class="custom-button">
                                    <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-5">
            <div class="card mb-3">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/analyzer.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Analyse Performance</h5>
                            <p class="card-text">Check your results here!</p>
                            <p class="card-text">
                                <small class="text-muted">
                                    <a href="/view/analysis" class="custom-button">
                                        <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                    </a>
                                </small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>










.card {
    /* border-radius  : 20px;
    height         : 170px; */
    border-radius        : 1.5rem;
    height               : 100%;
    width                : auto;
    /* margin-top        : 30px; */
    /* margin            : 1.5rem; */
    object-fit           : cover;
    display              : block;
    align-items          : center;
    justify-content      : center;
}

.card-img {
    /* position: relative;
    padding : 10px;
    width   : 100%;
    height  : auto; */

    padding: 1rem;
}

.custom-button {
    position: absolute;
    right   : 0%;
    bottom  : 0%;
}

div.custom-card {
    width  : 30rem;
    height : 10rem;
    padding: 1rem 1rem 1rem 1rem;
    display: block;
}

div.custom-card a img {
    width        : 8rem;
    height       : 8rem;
    padding      : 1.5rem;
    border-radius: 2rem;
    box-shadow   : inset 0px 0px 10px black;
    float        : left;
}

div.custom-card a span.custom-card-main-text {
    font-size   : 1.5em;
    padding-top : 2rem;
    padding-left: 2rem;

}











    <!-- <div class="shadow-lg custom-card">
        <a href="">
            <img src="/static/images/analyzer.svg" class="card-img" alt="...">
            <span class="custom-card-main-text">Analyse</span>
            <br>
            <span class="custom-card-subtext">Analyse</span>
        </a>
    </div> -->





    <div class="row">
        <div class="col-md-5">
            <div class="card">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/orchestrator.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Orchestrator</h5>
                            <p class="card-text">Are you a trusted third party looking to orchestrate your
                                own federated cycle?</p>
                            <p class="card-text">
                                <a href="/orchestrator" class="custom-button">
                                    <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-5">
            <div class="card mb-3">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/participant.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Participant</h5>
                            <p class="card-text">Are you an individual or organisation looking to enroll in an existing
                                collaboration?</p>
                            <p class="card-text">
                                <a href="/participant" class="custom-button">
                                    <i class="fa bi-arrow-right-circle-fill fa-2x"></i>
                                </a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>






    <div class="row">

        <!-- Profile Metadata Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/participant/profiles">
                <div class="row no-gutters">
                    <div class="col-md-3">
                        <img src="/static/images/participant.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Profile</h5>
                            <p class="card-text">Content management</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Registration Metadata Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/participant/registrations">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/registration.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Registrations</h5>
                            <p class="card-text">Entering partnerships</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

    </div>

    <h3 class="title" id="participant-header">Actions</h3>

    <div class="row">
       
        <!-- Inference Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/participant/inferences">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/inference.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Predict</h5>
                            <p class="card-text">Conduct inferences</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>
        
    </div>


/* #custom-card {
    margin : 1rem;
    width  : 25rem;
    height : 7rem;
    padding: 1rem;
    display: block;
}

#custom-card h5.card-title {
    font-weight: bold;
    color      : black;
}

#custom-card p.card-text {
    font-weight: normal;
    color      : black;
}

#custom-card:hover h5.card-title {
    color          : #d87f4d;
    font-size      : 150%;
    text-decoration: underline;
}

#custom-card:hover p.card-text {
    color: #d87f4d;
}

#custom-card img.card-img {
    display      : block;
    margin-left  : auto;
    margin-right : auto;
    width        : 5rem;
    height       : 5rem;
    padding      : 1rem;
    border-radius: 1px;
    box-shadow   : 0px 0px 10px rgb(223, 222, 222);
} */



/* #custom-card div.card-body {
    margin-left: auto;
    margin-right: auto;
} */


/* .css-1s8nojw {
    padding-top: 4rem;
    background-color: #edf2ef;
    border-radius: 1.5rem;
} */

.stSidebar div[class^='st-'] {
    background-color: yellow;
}

.main div[class^='st-'] {
    background-color: white;
} */

.reportview-container div[class^="css-"]>div[class^='st-']{
    background-color: yellow;
}


                    //for making parent of submenu active
                    $(this).closest("li").parent().parent().addClass("active");













.menu-logo .logo-content img {
    width                : 3.8rem;
    height               : 3.8rem;
    /* position          : fixed; */
    /* object-fit        : contain; */
    -webkit-transition   : all .1s linear;
    transition           : all .1s linear;
}




/* .fa {
    position      : relative;
    display       : table-cell;
    width         : 4rem;
    height        : 2rem;
    text-align    : center;
    vertical-align: middle;
    font-size     : 1.5rem;
} */

.main-menu .nav-icon {
    /* position      : relative; */
    display       : table-cell;
    width         : 4rem;
    height        : 2rem;
    text-align    : center;
    vertical-align: middle;
    font-size     : 1.2rem;
}

.main-menu .nav-text {
    position      : relative;
    display       : table-cell;
    vertical-align: middle;
    width         : 10rem;
    font-family   : 'Titillium Web', sans-serif;
}

.main-menu>ul.helpline {
    position: absolute;
    left    : 0;
    bottom  : 0;
}

a:hover,
a:focus {
    text-decoration: none;
}

nav {
    -webkit-user-select: none;
    -moz-user-select   : none;
    -ms-user-select    : none;
    -o-user-select     : none;
    user-select        : none;
}

nav ul,
nav li {
    outline    : 0;
    margin     : 0;
    padding    : 0;
    line-height: 4rem;
}

nav.main-menu {
    border-top-right-radius   : 1.5rem;
    border-bottom-right-radius: 1.5rem;
}

nav.main-menu:not(:hover) li.active>a {
    color           : #ffffff;
    background-color: #d87f4d;
}

nav.main-menu:hover li:hover>a {
    background-color: #d87f4d;
    border-top-right-radius: 3rem;
    border-bottom-right-radius: 3rem;
}





<nav class="navbar fixed-top shadow-sm navbar-light" id="selection">
    <span class="navbar-text" id="selection_back_text">
        <a href="/home">
            <i class="fa bi-arrow-left-short fa-2x">Home</i>
        </a>
    </span>
</nav>


















@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap');

body {
    font-family     : 'Poppins', sans-serif;
    font-weight     : normal;
    margin          : 0;
    background-color: #ffffff;
}

.home-page {
    padding   : 0 3rem;
    max-height: 100%;
    height    : auto;
    overflow-y: auto;
}

.title, .header {
    margin-top   : 3rem;
    margin-bottom: 1rem;
}

.header {
    color: #878787;
}

#custom-card {
    margin : 1rem;
    width  : 25rem;
    height : 10rem;
    padding: 1rem;
    display: block;
}

#custom-card h5.card-title {
    font-weight: bold;
    color      : black;
}

#custom-card p.card-text {
    font-weight: normal;
    color      : black;
}

#custom-card:hover h5.card-title {
    color          : #d87f4d;
    font-size      : 150%;
    text-decoration: underline;
}

#custom-card:hover p.card-text {
    color: #d87f4d;
}

#custom-card img.card-img {
    width        : 8rem;
    height       : 8rem;
    padding      : 1.5rem;
    border-radius: 2rem;
    box-shadow   : inset 0px 0px 10px black;
}






<div class="ttp-page">
    <h1 class="title" id="ttp-title">Orchestrator Dashboard</h1>

    <div class="row">

        <!-- Collaboration Metadata Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/orchestrator/collaborations">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/collaboration.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Collaborations</h5>
                            <p class="card-text">Deployment configurations</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Project Metadata Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/orchestrator/projects">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/project.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Projects</h5>
                            <p class="card-text">Dataset variants</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Experiment Metadata Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/orchestrator/experiments">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/experiment.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Experiments</h5>
                            <p class="card-text">Model architectures</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Run Metadata Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/orchestrator/runs">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/run.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Runs</h5>
                            <p class="card-text">Hyperparameter sets</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

    </div>

    <h3 class="title" id="ttp-header">Performance Actions</h3>

    <div class="row">

        <!-- Optimization Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/orchestrator/optimizations">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/optimizer.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Optimize</h5>
                            <p class="card-text">Tune your models!</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Analysis Pipeline -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/view/orchestrator/analysis">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/analyzer.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Analyse</h5>
                            <p class="card-text">Check your results here!</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>
        
    </div>
</div>


























<div class="home-page">
    <h1 class="title" id="home-title">Welcome to Synergos Portal</h1>

    <!-- Dashboard Section -->
    <h4 class="header" id="dashboard-header">Dashboards</h4>

    <div class="row">

        <!-- Orchestrator Dashboard -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/orchestrator">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/orchestrator.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Orchestrator</h5>
                            <p class="card-text">Trusted Third Parties</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>

        <!-- Participant Dashboard -->
        <div class="card mb-3 border-0" id="custom-card">
            <a href="/participant">
                <div class="row no-gutters">
                    <div class="col-md-4">
                        <img src="/static/images/participant.svg" class="card-img" alt="...">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">Participant</h5>
                            <p class="card-text">Contributing individuals or organizations</p>
                        </div>
                    </div>
                </div>
            </a>
        </div>
    </div>

    <!-- Resources Section -->
    <h4 class="header" id="resources-header">Resources</h4>

    <div class="card-deck">
        <div class="card">
            <img src="..." class="card-img-top" alt="...">
            <div class="card-body">
                <h5 class="card-title">Card title</h5>
                <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional
                    content. This content is a little bit longer.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">Last updated 3 mins ago</small>
            </div>
        </div>
        <div class="card">
            <img src="..." class="card-img-top" alt="...">
            <div class="card-body">
                <h5 class="card-title">Card title</h5>
                <p class="card-text">This card has supporting text below as a natural lead-in to additional content.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">Last updated 3 mins ago</small>
            </div>
        </div>
        <div class="card">
            <img src="..." class="card-img-top" alt="...">
            <div class="card-body">
                <h5 class="card-title">Card title</h5>
                <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional
                    content. This card has even longer content than the first to show that equal height action.</p>
            </div>
            <div class="card-footer">
                <small class="text-muted">Last updated 3 mins ago</small>
            </div>
        </div>
    </div>
    
</div>



.home-page {
    padding   : 0 3rem;
    max-height: 100%;
    height    : auto;
    overflow-y: auto;
}

.title, .header {
    margin-top   : 3rem;
    margin-bottom: 1rem;
}

.header {
    color: #878787;
}

#custom-card {
    margin : 1rem;
    width  : 25rem;
    height : 10rem;
    padding: 1rem;
    display: block;
}

#custom-card h5.card-title {
    font-weight: bold;
    color      : black;
}

#custom-card p.card-text {
    font-weight: normal;
    color      : black;
}

#custom-card:hover h5.card-title {
    color          : #d87f4d;
    font-size      : 150%;
    text-decoration: underline;
}

#custom-card:hover p.card-text {
    color: #d87f4d;
}

#custom-card img.card-img {
    width        : 8rem;
    height       : 8rem;
    padding      : 1.5rem;
    border-radius: 2rem;
    box-shadow   : inset 0px 0px 10px black;
}






















/* #selection {
    position     : relative;
    white-space  : nowrap;
    display      : flexbox;
    align-content: center;
}

#selection .navbar-text {
    padding-left: 1rem;
}

#selection .navbar-text a {
    display    : flex;
    align-items: center;
    font-size  : 1.2rem;
} */

<!-- <nav class="navbar fixed-top shadow-sm navbar-light" id="selection">
    <span class="navbar-text" id="selection_back_text">
        <a href="/home">
            <i class="fa bi-arrow-left-short fa-2x"></i>
            <span>Home</span>
        </a>
    </span>
</nav> -->




















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

    if option == SUPPORTED_ACTIONS[0]:
        create_collaborations(driver)

    elif option == SUPPORTED_ACTIONS[1]:
        browse_collaborations(driver)

    elif option == SUPPORTED_ACTIONS[2]:
        update_collaborations(driver)

    elif option == SUPPORTED_ACTIONS[3]:
        remove_collaborations(driver)


def app():
    """ Main app orchestrating project management procedures """
    option = st.sidebar.selectbox(
        label='Select action to perform:', 
        options=SUPPORTED_ACTIONS,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    driver = render_orchestrator_inputs()

    combination_key = render_upstream_hierarchy(r_type=R_TYPE, driver=driver)

    if option == SUPPORTED_ACTIONS[0]:
        create_projects(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[1]:
        browse_projects(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[2]:
        update_projects(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[3]:
        remove_projects(driver, combination_key)


def app():
    """ Main app orchestrating experiment management procedures """
    option = st.sidebar.selectbox(
        label='Select action to perform:', 
        options=SUPPORTED_ACTIONS,
        help="State your role for your current visit to Synergos. Are you a \
            trusted third party (i.e. TTP) looking to orchestrate your own \
            federated cycle? Or perhaps a participant looking to enroll in an \
            existing collaboration?"
    )

    driver = render_orchestrator_inputs()

    combination_key = render_upstream_hierarchy(r_type=R_TYPE, driver=driver)

    if option == SUPPORTED_ACTIONS[0]:
        create_experiments(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[1]:
        browse_experiments(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[2]:
        update_experiments(driver, combination_key)

    elif option == SUPPORTED_ACTIONS[3]:
        remove_experiments(driver, combination_key)











if __name__ == '__main__':
    st.markdown("""
                ## How to download files in Streamlit with download_button()
                ~> Below are use cases and code examples for the `download_button()`
                function, which returns a clickable download link given your data
                file as input.
                See the `Show code example` at the bottom of each section for a
                code snippet you can copy & paste.
                [Recommend improvements here](https://discuss.streamlit.io/)
                The download_button() function is an extension of a workaround based on
                the discussions covered in more detail at [Awesome Streamlit](http://awesome-streamlit.org/).
                Go to Gallery -> Select the App Dropdown -> Choose "File Download Workaround"
                for more information.""")

    st.markdown('-'*17)


    # ---------------------
    # Download from memory
    # ---------------------
    if st.checkbox('Download object from memory'):
        st.write('~> Use if you want to save some data from memory (e.g. pd.DataFrame, dict, list, str, int)')

        # Enter text for testing
        s = st.selectbox('Select dtype', ['list',  # TODO: Add more
                                          'str',
                                          'int',
                                          'float',
                                          'dict',
                                          'bool',
                                          'pd.DataFrame'])
        
        filename = st.text_input('Enter output filename and ext (e.g. my-dataframe.csv, my-file.json, my-list.txt)', 'my-file.json')

        # Pickle Rick
        pickle_it = st.checkbox('Save as pickle file')

        sample_df = pd.DataFrame({'x': list(range(10)), 'y': list(range(10))})
        sample_dtypes = {'list': [1,'a', [2, 'c'], {'b': 2}],
                         'str': 'Hello Streamlit!',
                         'int': 17,
                         'float': 17.0,
                         'dict': {1: 'a', 'x': [2, 'c'], 2: {'b': 2}},
                         'bool': True,
                         'pd.DataFrame': sample_df}

        # Display sample data
        st.write(f'#### Sample `{s}` to be saved to `{filename}`')
        st.code(sample_dtypes[s], language='python')

        # Download sample
        download_button_str = download_button(sample_dtypes[s], filename, f'Click here to download {filename}', pickle_it=pickle_it)
        st.markdown(download_button_str, unsafe_allow_html=True)

        if st.checkbox('Show code example '):
            code_text = f"""
                        s = {sample_dtypes[s]}
                        download_button_str = download_button(s, '{filename}', 'Click here to download {filename}', pickle_it={pickle_it})
                        st.markdown(download_button_str, unsafe_allow_html=True)"""

            st.code(code_text, language='python')

    # --------------------------
    # Select a file to download
    # --------------------------
    if st.checkbox('Select a file to download'):
        st.write('~> Use if you want to test uploading / downloading a certain file.')

        # Upload file for testing
        folder_path = st.text_input('Enter directory: deafult .', '.')
        filename = file_selector(folder_path=folder_path)

        # Load selected file
        with open(filename, 'rb') as f:
            s = f.read()

        download_button_str = download_button(s, filename, f'Click here to download {filename}')
        st.markdown(download_button_str, unsafe_allow_html=True)

        if st.checkbox('Show code example'):
            code_text = f"""
                        with open('{filename}', 'rb') as f:
                            s = f.read()
                        download_button_str = download_button(s, '{filename}', 'Click here to download {filename}')
                        st.markdown(download_button_str, unsafe_allow_html=True)"""

            st.code(code_text, language='python')



















class MultiApp:
    """ Framework for combining multiple streamlit applications.
    
    Usage:
        def foo():
            st.title("Hello Foo")
        def bar():
            st.title("Hello Bar")
        app = MultiApp()
        app.add_app("Foo", foo)
        app.add_app("Bar", bar)
        app.run()
    
    It is also possible keep each application in a separate file.
        import foo
        import bar
        app = MultiApp()
        app.add_app("Foo", foo.app)
        app.add_app("Bar", bar.app)
        app.run()
    """
    def __init__(self):
        self.apps = {}

    ###########
    # Helpers #
    ###########

    def add_app(self, action: str, func: Callable):
        """ Adds a new application view, mapped to a specific action.

        Args:
            action (str): Keyword trigger
            func (Callable): Python function to render this app.
        """
        self.apps[action] = func

    ##################
    # Main Functions #
    ##################

    def run(self, action: str):
        selected_title = st.sidebar.selectbox(
            'What do you want to do?',
            list(self.apps.keys())
        )
        app = self.apps[selected_title]
        app()













<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item">
            <a href="/{{role}}"><span>{{role | capitalize}}</span></a>
        </li>
        <li class="breadcrumb-item">
            <a href="/actions/{{role}}/{{resource}}"><span>Manage {{resource | capitalize}}</span></a>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
            <span>{{action | capitalize}} {{resource | capitalize}}</span>
        </li>
    </ol>
</nav>








###################
# Styling Helpers #
###################

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    


def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True) 























def render_collaborations(driver: Driver = None, show_details: bool = True):
    """ Renders out retrieved collaboration metadata in a custom form 

    Args:
        driver (Driver): A connected Synergos driver to communicate with the
            selected orchestrator.
        show_details (bool): Toogles if collaboration details should be shown 
    Returns:
        Selected collaboration ID    (str)
        Updated collaboration record (dict)
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
            help="Select a collaboration to peruse."
        )

        if not show_details:
            return selected_collab_id, None
            
        if driver:
            selected_collab_data = driver.collaborations.read(
                collab_id=selected_collab_id
            ).get('data', {})
        else:
            selected_collab_data = {}
        
        if selected_collab_data:
            selected_collab_data.pop('relations')   # no relations rendered!

        with st.beta_expander("Collaboration Details"):
            updated_collab = collab_renderer.display(selected_collab_data)

    return selected_collab_id, updated_collab



















html,
body {
    height: 100%;
}

body {
    background: linear-gradient(to right, rgba(19, 19, 20, 0.52), rgba(109, 90, 5, 0.73)),
        url('/static/images/synergos_landing_background.svg') no-repeat center center fixed;
    -webkit-background-size: cover;
    -moz-background-size   : cover;
    -o-background-size     : cover;
    background-size        : cover;
    display                : flex;
    align-items            : left;
}

.btn {
    border-radius: 2rem;
}







.intro-block .intro-content:hover {
    animation-name              : collapse;
    animation-duration          : 1s;
    /* animation-iteration-count: infinite; */
    /* linear | ease | ease-in | ease-out | ease-in-out */
    animation-timing-function   : linear;
    animation-play-state        : paused;
}









/* .resources .carousel .carousel-item {
    height: 25rem;
}

.resources .carousel .carousel-item .card {
    position: relative;
    height  : 100vh;
} */

/* .carousel-item img {
    position: absolute;
    object-fit:cover;
    top: 0;
    left: 0;
    min-height: 15rem;
} */

/* .carousel-inner {
    max-height: 25rem !important;
}

.carousel-item,
.card {
    position  : relative;
    max-height: 100%;
    max-width : 100%;
} */











        // const numClicks = ref(0)
        // const onClicked = () => {
        //     numClicks.value++
        //     Streamlit.setComponentValue(numClicks.value)
        // }

        // return {
        //     numClicks,
        //     onClicked,
        // }












    # st.markdown(
    #     """
    #     <style>
    #     #streamlit-content {
    #         margin-top: .4rem;
    #         width     : 90vw;
    #         height    : 90vh;
    #         position  : relative;
    #         overflow: hidden;
    #     }
    #     </style>

    #     <body>
    #     <div class="css-1y0tads">
    #         <iframe src="http://localhost:8080/" id="streamlit-content" allowfullscreen
    #             frameborder="0" wmode="transparent">
    #             Your browser doesn't support iframes
    #         </iframe>
    #     </div>
    #     <body>
    #     """,
    #     unsafe_allow_html=True
    # )

    # st.markdown(
    #     """
    #     <script>
    #     var injection = '''
    #         <iframe src="http://localhost:8080/?p=hello" id="streamlit-content" allowfullscreen
    #             frameborder="0" wmode="transparent">
    #             Your browser doesn't support iframes
    #         </iframe>
    #     '''
    #     $(injection).insertBefore("section");

    #     </script>
    #     """,
    #     unsafe_allow_html=True
    # )




















    <template>
    <div class="container">
        <!-- <span>
            Hello, {{ args.name }}! &nbsp;
            <button @click="onClicked">Click Me!</button>
        </span> -->
        <input type="checkbox" v-model="draggable" /> Draggable
        <input type="checkbox" v-model="resizable" /> Resizable
        <input type="checkbox" v-model="responsive" /> Responsive
        <br />
        <div style="width: 100%; margin-top: 10px; height: 100%">
            <grid-layout
                v-model="layout"
                :col-num="12"
                :row-height="30"
                :is-draggable="draggable"
                :is-resizable="resizable"
                :responsive="responsive"
                :vertical-compact="true"
                :use-css-transforms="true"
            >
                <grid-item
                    v-for="item in layout"
                    :static="item.static"
                    :x="item.x"
                    :y="item.y"
                    :w="item.w"
                    :h="item.h"
                    :i="item.i"
                    :key="item.i"
                >
                    <span class="text">{{ item.i }}</span>
                    <iframe
                        src="http://localhost:15672/"
                        id="rmq"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item>
            </grid-layout>
        </div>
    </div>
</template>


<script>
// import { ref } from "vue"
// import { Streamlit } from "streamlit-component-lib"
import { GridLayout, GridItem } from "vue-grid-layout"
// import { useStreamlit } from "../streamlit"

export default {
    name: "CommandStation",
    components: {
        GridLayout,
        GridItem,
    },
    props: ["args"],   // Arguments that are passed to the plugin in Python are accessible in prop "args"
    // setup() {
    //     useStreamlit() // lifecycle hooks for automatic Streamlit resize
    // },
    data() {
        return {
            layout: [
                { x: 0, y: 0, w: 4, h: 8, i: "0" },
                { x: 4, y: 0, w: 4, h: 8, i: "1" },
                { x: 8, y: 0, w: 4, h: 8, i: "2" },

                // { x: 0, y: 8, w: 4, h: 8, i: "3" },
                // { x: 4, y: 16, w: 4, h: 8, i: "4" },
                // { x: 8, y: 24, w: 4, h: 8, i: "5" },

                // { x: 0, y: 8, w: 4, h: 8, i: "6" },
                // { x: 4, y: 16, w: 4, h: 8, i: "7" },
                // { x: 8, y: 24, w: 4, h: 8, i: "8" },

                // { x: 0, y: 8, w: 4, h: 8, i: "9" },
                // { x: 4, y: 16, w: 4, h: 8, i: "10" },
                // { x: 8, y: 24, w: 4, h: 8, i: "11" },

                // { x: 0, y: 8, w: 4, h: 8, i: "12" },
                // { x: 4, y: 16, w: 4, h: 8, i: "13" },
                // { x: 8, y: 24, w: 4, h: 8, i: "14" },

                // { x: 0, y: 8, w: 4, h: 8, i: "15" },
                // { x: 4, y: 16, w: 4, h: 8, i: "16" },
                // { x: 8, y: 24, w: 4, h: 8, i: "17" },

                // { x: 0, y: 8, w: 4, h: 8, i: "17" },
                // { x: 4, y: 16, w: 4, h: 8, i: "18" },
                // { x: 8, y: 24, w: 4, h: 8, i: "19" },

                // { x: 0, y: 8, w: 4, h: 8, i: "20" },
                // { x: 4, y: 16, w: 4, h: 8, i: "21" },
                // { x: 8, y: 24, w: 4, h: 8, i: "22" },

                // { x: 0, y: 8, w: 4, h: 8, i: "23" },
                // { x: 4, y: 16, w: 4, h: 8, i: "24" },
                // { x: 8, y: 24, w: 4, h: 8, i: "25" },
            ],
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        }
    },
}
</script>


<style scoped>
.vue-grid-layout {
    background: #eee;
}
.vue-grid-item:not(.vue-grid-placeholder) {
    background: #ccc;
    border: 1px solid black;
}
.vue-grid-item .resizing {
    opacity: 0.9;
}
.vue-grid-item .static {
    background: #cce;
}
.vue-grid-item .text {
    font-size: 24px;
    text-align: center;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
    height: 100%;
    width: 100%;
}
.vue-grid-item .no-drag {
    height: 100%;
    width: 100%;
}
.vue-grid-item .minMax {
    font-size: 12px;
}
.vue-grid-item .add {
    cursor: pointer;
}
.vue-draggable-handle {
    position: absolute;
    width: 20px;
    height: 20px;
    top: 0;
    left: 0;
    background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>")
        no-repeat;
    background-position: bottom right;
    padding: 0 8px 8px 0;
    background-repeat: no-repeat;
    background-origin: content-box;
    box-sizing: border-box;
    cursor: pointer;
}
.layoutJSON {
    background: #ddd;
    border: 1px solid black;
    margin-top: 10px;
    padding: 10px;
}
.columns {
    -moz-columns: 120px;
    -webkit-columns: 120px;
    columns: 120px;
}

#rmq {
    margin-top: 0.4rem;
    width: 100%;
    height: 100%;
    position: relative;
}
</style>



















<!-- 
  We bootstrap our Component to Streamlit with our scoped slot in the top-level App.
  This is where scoped slot passes Streamlit `args` data from itself to children MyComponent.
  You should not have to edit this, but are free to do so :)
-->
<template>
    <div id="app">
        <!-- <WithStreamlitConnection v-slot="{ args }">
            <CommandStation :args="args" />
        </WithStreamlitConnection> -->
        <CommandStation />
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"
import CommandStation from "./components/CommandStation.vue"

// "withStreamlitConnection" is a scoped slot. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
// import WithStreamlitConnection from "./streamlit/WithStreamlitConnection.vue"

export default defineComponent({
    name: "App",
    components: {
        CommandStation,
        // WithStreamlitConnection,
    },
})
</script>

<style>
/* body {
    margin: 0;
} */
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
}
</style>














































<!-- 
  We bootstrap our Component to Streamlit with our scoped slot in the top-level App.
  This is where scoped slot passes Streamlit `args` data from itself to children MyComponent.
  You should not have to edit this, but are free to do so :)
-->
<template>
    <div id="app">
        <WithStreamlitConnection v-slot="{ args }">
            <MyComponent :args="args" />
        </WithStreamlitConnection>
    </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"
import MyComponent from "./MyComponent.vue"

// "withStreamlitConnection" is a scoped slot. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
import WithStreamlitConnection from "./streamlit/WithStreamlitConnection.vue"

export default defineComponent({
    name: "App",
    components: {
        MyComponent,
        WithStreamlitConnection,
    },
})
</script>

<style>
body {
    margin: 0;
}
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
}
</style>












    "@typescript-eslint/eslint-plugin": "^2.33.0",
    "@typescript-eslint/parser": "^2.33.0",
    "@vue/cli-plugin-babel": "~4.5.0",
    "@vue/cli-plugin-eslint": "~4.5.0",
    "@vue/cli-plugin-typescript": "^4.5.0",
    "@vue/cli-service": "~4.5.0",
    "@vue/compiler-sfc": "^3.0.0-0",
    "@vue/eslint-config-typescript": "^5.0.2",
    "babel-eslint": "^10.1.0",
    "eslint": "^6.7.2",
    "eslint-plugin-vue": "^7.0.0-0",
    "typescript": "~3.9.3"















    const renderData = ref<RenderData>((undefined as unknown) as RenderData)










    /* .css-1y0tads+iframe {
    width   : 100vw !important;
    height  : 100vh !important;
    padding : 0;
    position: fixed;
} */

/* .section[data-testid="stSidebar"][aria-expanded=true] + .css-1y0tads,
.section[data-testid="stSidebar"][aria-expanded=true] + iframe {
    height  : 100vh !important;
    width   : auto !important;
    padding : 0;
    position: fixed;
} */

/* .section[data-testid="stSidebar"]:not([aria-expanded=True]) + .css-1y0tads {
    padding : 0 !important;
} */

/* section[data-testid="stSidebar"][aria-expanded=True] + div.block-container,
section[data-testid="stSidebar"][aria-expanded=True] + div.main,
section[data-testid="stSidebar"][aria-expanded=True] + div.css-1y0tads
section[data-testid="stSidebar"][aria-expanded=True] + div.eknhn3m2
section[data-testid="stSidebar"][aria-expanded=True] + div.css-1v3fvcr {
    padding : 0 !important;
    position: absolute !important;
} */















[data-testid="stDecoration"] {
    height : 0 !important;
    display: none !important;
}

/* Full screen IFrame from SynUI-Tracker (when sidebar is expanded) */
section[data-testid="stSidebar"][aria-expanded=true]+section.main,
section[data-testid="stSidebar"][aria-expanded=true]+section.eknhn3m1,
section[data-testid="stSidebar"][aria-expanded=true]+section.css-1v3fvcr {
    height  : 100vh !important;
    width   : calc(100vw - 21rem) !important;
    margin  : 0 0 0 21rem !important;
    padding : 0 !important;
    position: absolute !important;
}

section[data-testid="stSidebar"][aria-expanded=true]+section>div.block-container,
section[data-testid="stSidebar"][aria-expanded=true]+section>div.css-1y0tads,
section[data-testid="stSidebar"][aria-expanded=true]+section>div.eknhn3m2 {
    height  : 100% !important;
    width   : 100% !important;
    padding : 0 !important;
    position: relative !important;
}

/* Full screen IFrame from SynUI-Tracker (when sidebar is collapsed) */
section[data-testid="stSidebar"][aria-expanded=false]+section.main,
section[data-testid="stSidebar"][aria-expanded=false]+section.eknhn3m1,
section[data-testid="stSidebar"][aria-expanded=false]+section.css-1v3fvcr {
    height  : 100vh !important;
    width   : 100vw !important;
    padding : 0 !important;
    position: absolute !important;
}

section[data-testid="stSidebar"][aria-expanded=false]+section>div.block-container,
section[data-testid="stSidebar"][aria-expanded=false]+section>div.css-1y0tads,
section[data-testid="stSidebar"][aria-expanded=false]+section>div.eknhn3m2 {
    height  : 100% !important;
    width   : 100% !important;
    padding : 0 !important;
    position: relative !important;
}


/* section iframe[id]:not([id="streamlit-content"]) {
    width   : 100% !important;
    height  : 100% !important;
    position: relative !important;
} */

/* section[data-testid="stSidebar"][aria-expanded=True] + div.css-1y0tads */
/* section[data-testid="stSidebar"][aria-expanded=True] + div.eknhn3m2 */

/* a[aria-expanded="true"]{
    background-color: #42DCA3;
  } */




















  def read_production_css() -> str:
    """ Helper function that loads in and combines all static CSS files 
        declared as a HTML tag string. This is a temporary hack to inject
        custom designs & formats into Streamlit

    Returns:
        Production style tag (str)   
    """
    prod_css_globstring = os.path.join(STYLES_DIR, "**", "*.css") 
    style_paths = glob(prod_css_globstring)

    loaded_styles = []
    for style_path in style_paths:

        with open(style_path, "r") as pcp:
            curr_styles = pcp.read()
            loaded_styles.append(curr_styles)

    production_styles = "<style>{}</style>".format('\n'.join(loaded_styles)) 

    return production_styles










    # components.html(
    #     """
    #     <style>
    #     #streamlit-content {
    #         margin-top: .4rem;
    #         width     : 90vw;
    #         height    : 90vh;
    #         position  : relative;
    #         overflow  : hidden;
    #     }
    #     </style>

    #     <body>

    #         <iframe src="http://localhost:8080/" id="streamlit-content" allowfullscreen
    #             frameborder="0" wmode="transparent">
    #             Your browser doesn't support iframes
    #         </iframe>
    #     <body>
    #     """
    # )
    












        // logs(this: any) {
        //     const name = this.args.logs.name;
        //     const host = this.args.logs.host;
        //     const port = this.args.logs.port;
        //     const url = `http://${host}:${port}`;
        //     return { name: name, url: url };
        // },

        // component(this: any) {
        //     const name = this.args.logs.name;
        //     const host = this.args.logs.host;
        //     const port = this.args.logs.port;
        //     const url = `http://${host}:${port}`;
        //     return { name: name, url: url };
        // },





def commence_jobs(driver: Driver = None, filters: Dict[str, str] = {}):
    """
    """
    st.title("Orchestrator - Submit a Federated Job")

    # Extract individual keys
    filtered_collab_id = filters.get('collab_id', None)
    filtered_project_id = filters.get('project_id', None)
    filtered_expt_id = filters.get('expt_id', None)
    filtered_run_id = filters.get('run_id', None)  

    # A. Filter out relevant collaborations
    if driver and not filtered_collab_id:
        all_collabs = driver.collaborations.read_all().get('data', [])
        collab_ids = [collab['key']['collab_id'] for collab in all_collabs]

    elif driver and filtered_collab_id:
        collab_ids = [filtered_collab_id]

    else:
        collab_ids = []

    federated_jobs = []
    for collab_id in collab_ids:

        # B. Filter out relevant projects
        if driver and not filtered_project_id:
            all_projects = driver.projects.read_all(
                collab_id=collab_id
                ).get('data', [])
            project_ids = [project['key']['project_id'] for project in all_projects]
        
        elif driver and filtered_project_id:
            project_ids = [filtered_project_id]

        else:
            project_ids = []

        for project_id in project_ids:

            # C. Filter out relevant experiments
            if driver and not filtered_expt_id:
                all_expts = driver.experiments.read_all(
                    collab_id=collab_id, 
                    project_id=project_id
                    ).get('data', [])
                expt_ids = [expt['key']['expt_id'] for expt in all_expts]
            
            elif driver and filtered_expt_id:
                expt_ids = [filtered_expt_id]

            else:
                expt_ids = []

            for expt_id in expt_ids:

                # D. Filter out relevant runs
                if driver and not filtered_run_id:
                    all_runs = driver.runs.read_all(
                        collab_id=collab_id, 
                        project_id=project_id, 
                        expt_id=expt_id
                        ).get('data', [])
                    job_keys = [run['key'] for run in all_runs]
                
                elif driver and filtered_run_id:
                    run = driver.runs.read(
                        collab_id=collab_id, 
                        project_id=project_id, 
                        expt_id=expt_id, 
                        run_id=filtered_run_id
                        ).get('data', {})
                    job_keys = [run['key']]

                else:
                    job_keys = []

                federated_jobs += job_keys

    # List out all collaborations in hierarchy
    for _idx, job_key in enumerate(federated_jobs):
        
        with st.beta_container():
            st.markdown("---")

            columns = st.beta_columns((1, 1.5))
            
            with columns[0]:
                st.text_input(
                    label="Collaboration ID:", 
                    value=job_key.get('collab_id', ""),
                    key=f"collab_{_idx}"
                )
                st.text_input(
                    label="Project ID:", 
                    value=job_key.get('project_id', ""),
                    key=f"project_{_idx}"
                )
                st.text_input(
                    label="Experiment ID:", 
                    value=job_key.get('expt_id', ""),
                    key=f"experiment_{_idx}"
                )
                st.text_input(
                    label="Run ID:", 
                    value=job_key.get('run_id', ""),
                    key=f"run_{_idx}"
                )
               
                # Check if model corresponding to job key exists 
                # (i.e. training has completed)
                trained_model = driver.models.read(**job_key).get('data', {})
                valid_stats = driver.validations.read(**job_key).get('data', {})

                status = st.text_input(
                    label="Status:", 
                    key=f"status_{_idx}", 
                    value=("completed" if (trained_model and valid_stats) else "idle")
                )

                if status == "idle":

                    st.markdown("") # buffer spacing

                    is_auto_aligned = st.checkbox(
                        label="Perform state auto-alignment",
                        value=True,
                        key=f"auto_align_{_idx}"
                    )
                    is_auto_fixed = st.checkbox(
                        label="Perform architecture auto-fixing",
                        value=True,
                        key=f"auto_fix_{_idx}"
                    )
                    is_logged = st.checkbox(
                        label="Display logs",
                        value=False,
                        key=f"log_msg_{_idx}"
                    )
                    is_verbose = False
                    if is_logged:
                        is_verbose = st.checkbox(
                            label="Use verbose view",
                            value=is_verbose,
                            key=f"verbose_{_idx}"
                        )

                    is_submitted = st.button(label="Start", key=f"start_{_idx}")
                    if is_submitted:

                        with st.spinner('Job in progress...'):

                            driver.alignments.create(
                                **job_key,
                                auto_align=is_auto_aligned,
                                auto_fix=is_auto_fixed
                            ).get('data', [])

                            driver.models.create(
                                **job_key,
                                auto_align=is_auto_aligned,
                                dockerised= True,
                                log_msgs=is_logged,
                                verbose=is_verbose
                            ).get('data', [])

                            driver.validations.create(
                                **job_key,
                                auto_align=is_auto_aligned,
                                dockerised= True,
                                log_msgs=is_logged,
                                verbose=is_verbose
                            ).get('data', [])

                        st.info("Job Completed! Please refresh to view results.")

                if status == 'completed':
                    action = st.radio(
                        label="Select an action:",
                        options=SUPPORTED_OPTIONS,
                        key=f"action_{_idx}"
                    )
                    
                    if action == SUPPORTED_OPTIONS[0]:
                        with columns[-1]:
                            with st.echo(code_location="below"):
                                st.write(valid_stats)

                    else:
                        filename = st.text_input(
                            label="Filename:",
                            value=f"RESULTS_{job_key['collab_id']}_{job_key['project_id']}_{job_key['expt_id']}_{job_key['run_id']}",
                            help="Specify a custom filename if desired"
                        )
                        download_name = f"{filename}.json"
                        download_tag = download_button(
                            object_to_download={
                                'models': trained_model,
                                'validations': valid_stats 
                            },
                            download_filename=download_name,
                            button_text="Download"
                        )
                        st.markdown(download_tag, unsafe_allow_html=True)












        val_data = project_data.get('relations', {}).get('Validation', [])
        avg_metrics = {}
        for val_record in val_data:
            
            expt_id = val_record.get('key', {}).get('expt_id')
            run_id = val_record.get('key', {}).get('run_id')

            val_stats = val_record.get('evaluate', {}).get('statistics', {})
            for metric, results in val_stats.items():

                if metric in target_metrics:
                    if isinstance(results, list) and results:
                        score = sum(results)/len(results)
                    elif isinstance(results, float):
                        score = results
                    else:
                        score = 0

                    expt_score_collection = avg_metrics.get(expt_id, {})
                    run_score_collection = expt_score_collection.get(run_id, {})
                
                    score_collection = run_score_collection.get(metric, [])
                    score_collection.append(score)

                    run_score_collection[metric] = score_collection
                    expt_score_collection[run_id] = run_score_collection
                    avg_metrics[expt_id] = expt_score_collection

        consolidated_avgs = {}
        for expt, expt_scores in avg_metrics.items():
            for run, run_scores in expt_scores.items():
                for metric, score_collection in run_scores.items():
                    grid_avg = sum(score_collection)/len(score_collection)
                    metric_collection = consolidated_avgs.get(metric, [])
                    metric_collection.append((expt, run, grid_avg))
                    consolidated_avgs[metric] = metric_collection





    id_buffer_length = 0
    for (expt_id, run_id, _) in best_metrics.values():
        curr_max_length = max(len(expt_id), len(run_id)) 
        if curr_max_length > id_buffer_length:
            id_buffer_length = curr_max_length


    id_buffer_length = next(iter(set([
        max(len(expt_id), len(run_id)) 
        for (expt_id, run_id, _) in best_metrics.values()
    ])))








    components.html(
        """
        <!-- Bootstrap CSS CDN -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css"
            integrity="sha384-B0vP5xmATw1+K9KRQjQERJvTumQW0nPEzvF6L/Z6nronJ3oUOFUFpCjEUQouq2+l" crossorigin="anonymous">
        
        <!-- Bootstrap JS CDN -->
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
            integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
            crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-Piv4xVNRyMGpqkS2by6br4gNJ7DXjqk09RmUpJ8jgGtD7zP9yug3goQfGII0yAns"
            crossorigin="anonymous"></script>
        
        <!-- Tab Bar -->
        <ul class="nav nav-tabs">
            <li class="nav-item">
                <a class="nav-link active" href="#">Active</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#">Link</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#">Link</a>
            </li>
            <li class="nav-item">
                <a class="nav-link disabled" href="#">Disabled</a>
            </li>
        </ul>

        <!- Tab Content ->
        <div class="tab-content" id="tabs">
            <div class="tab-pane" id="aaa">...Content...</div>
            <div class="tab-pane" id="bbb">...Content...</div>
            <div class="tab-pane" id="ccc">...Content...</div>
        </div>
        """,
        width=500,
        height=1000
    )


















    # "catalogue_host":""
    # "catalogue_port":0
    # "logger_host":"127.0.0.1"
    # "logger_ports":{
    # "sysmetrics":9100
    # "director":9200
    # "ttp":9300
    # "worker":9400
    # }
    # "meter_host":""
    # "meter_port":0
    # "mlops_host":""
    # "mlops_port":0
    # "mq_host":"127.0.0.1"
    # "mq_port":5672
    # "ui_host":""
    # "ui_port":0 















# SUPPORTED_DEFAULT_PROCESSES = {
#     # "Construct a deployment script": None
# }

# SUPPORTED_ORCHESTRATOR_PROCESSES = {
#     'collaborations': {'Manage collaboration(s)': collab_app},
#     'projects': {'Manage project(s)': project_app},
#     'experiments': {'Manage experiment(s)': expt_app},
#     "Manage run(s)": run_app,
#     "Submit federated job(s)": submit_app,
#     # "Analyse federated job(s)": analysis_app,
#     # "Optimize a model": None
# }

# SUPPORTED_PARTICIPANT_PROCESSES = {
#     "Manage your profile": participant_app,
#     "Manage your registrations": reg_app,
#     "Submit inference(s)": infer_app
# }














def render_cascading_filter(participant_id: str) -> Dict[str, str]:
    """ Renders a dynamic filter that allows users to traverse the federated
        job hierarchy

    Returns:
        Composite Filtering keys (dict)
    """
    with st.sidebar.beta_container():

        st.header("FILTERS")

        with st.beta_expander("Key Parameters", expanded=True):

            selected_collab_id = st.text_input(label="Collaboration ID:")

            selected_project_id = (
                st.text_input(label="Project ID:")
                if selected_collab_id
                else None
            )

            selected_expt_id = (
                st.text_input(label="Experiment ID:")
                if selected_project_id
                else None
            )

            selected_run_id = (
                st.text_input(label="Run ID:")
                if selected_expt_id
                else None
            )

    return {
        'collab_id': selected_collab_id, 
        'project_id': selected_project_id, 
        'expt_id': selected_expt_id, 
        'run_id': selected_run_id
    }













def app(action: str):
    """ Main app orchestrating collaboration management procedures """

    driver = render_orchestrator_inputs()

    with st.sidebar.beta_container():
        st.header("USER")

        with st.beta_expander("User Parameters", expanded=True):
            participant_id, _ = render_participant(
                driver=driver, 
                show_details=False
            )

    key_filters = render_cascading_filter()
    st.write(key_filters)

    commence_inference(
        driver=driver, 
        participant_id=participant_id,
        filters={}#key_filters    
    )





        st.header("FILTERS")

        with st.beta_expander("Key Parameters", expanded=True):

            pass















{
    "search_space": {
        "rounds": {"_type":"choice","_value":[1, 2]},
        "epochs": {"_type":"choice","_value":[1, 2]},
        "batch_size": {"_type":"choice", "_value": [450, 512]},
        "lr":{"_type":"choice","_value":[0.0001, 0.1]},
        "criterion":{"_type":"choice","_value":["NLLLoss"]},
        "mu":{"_type":"uniform","_value":[0.0, 1.0]},
        "base_lr":{"_type":"choice","_value":[0.00005]},
        "max_lr":{"_type":"choice","_value":[0.2]}
    },


    "backend": "tune",
    "scheduler": "ASHAScheduler",
    "searcher": "TuneBOHB",
    "optimize_mode": "max",
    "metric": "accuracy",
    "trial_concurrency": 1,
    "max_exec_duration": "1h",
    "max_trial_num": 10,
    "max_concurrent": 1,


    "is_remote": true,
    "use_annotation": true,
    "auto_align": true,
    "dockerised": true,
    "verbose": true,
    "log_msgs": true
}






                    <!-- <grid-item :x=0 :y=0 :w=4 :h=18 :i=0 :key="MQ">
                    <iframe
                        src="http://localhost:15672"
                        id="mq"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item>

                <grid-item :x=4 :y=0 :w=4 :h=12 :i=1 :key="Logs">
                    <iframe
                        src="http://127.0.0.1:9000"
                        id="logs"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item> -->














export default {
    name: "MyComponent",
    props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
    components: {
        GridLayout,
        GridItem,
    },
    data() {
        return {
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        };
    },
    computed: {

        // NOTE: "any" type is used because "args" is casted as "any" //

        ranks(this: any): Array<string> {
            const PRIORITY = ["Logs", "MLOps", "MQ", "Catalogue", "Meter"]
            const components = Object.keys(this.args)
            const ranks = PRIORITY.filter(value => components.includes(value));
            return ranks
        },

        layout(this: any): Layout {
            const oneComponent = [{ x: 0, y: 0, w: 12, h: 12, i: "0"}];
            const twoComponent = [
                { x: 0, y: 0, w: 8, h: 18, i: "0" },
                { x: 0, y: 0, w: 8, h: 18, i: "1" },
            ];
            const threeComponent = [
                { x: 0, y: 0, w: 8, h: 18, i: "0" },
                { x: 0, y: 0, w: 8, h: 18, i: "1" },
                { x: 0, y: 0, w: 8, h: 18, i: "2" },
            ];
            const fourComponent = [
                { x: 0, y: 0, w: 8, h: 18, i: "0" },
                { x: 0, y: 0, w: 8, h: 18, i: "1" },
                { x: 0, y: 0, w: 8, h: 18, i: "2" },
                { x: 0, y: 0, w: 8, h: 18, i: "3" },
            ];
            const fiveComponent = [
                { x: 0, y: 0, w: 8, h: 18, i: "0" },
                { x: 0, y: 0, w: 8, h: 18, i: "1" },
                { x: 0, y: 0, w: 8, h: 18, i: "2" },
                { x: 0, y: 0, w: 8, h: 18, i: "3" },
                { x: 0, y: 0, w: 8, h: 18, i: "4" },
            ];

            const COUNTMAP: { [componentCount: number]: Layout | [] } = {};
            COUNTMAP[0] = [];
            COUNTMAP[1] = oneComponent;
            COUNTMAP[2] = twoComponent;
            COUNTMAP[3] = threeComponent;
            COUNTMAP[4] = fourComponent;
            COUNTMAP[5] = fiveComponent;

            const noOfComponents = this.ranks.length;

            return COUNTMAP[noOfComponents];
        }
    },
    methods: {
        retrieveUrl(this: any, name: string): string {
            const url = this.args[name];
            return url;
        }
    },
};














export default {
    name: "MyComponent",
    props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
    components: {
        GridLayout,
        GridItem,
    },
    data(this: any) {
        const oneComponent = [{ x: 0, y: 0, w: 12, h: 12, i: "0" }];
        const twoComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
        ];
        const threeComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
            { x: 0, y: 0, w: 8, h: 18, i: "2" },
        ];
        const fourComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
            { x: 0, y: 0, w: 8, h: 18, i: "2" },
            { x: 0, y: 0, w: 8, h: 18, i: "3" },
        ];
        const fiveComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
            { x: 0, y: 0, w: 8, h: 18, i: "2" },
            { x: 0, y: 0, w: 8, h: 18, i: "3" },
            { x: 0, y: 0, w: 8, h: 18, i: "4" },
        ];

        const COUNTMAP: { [componentCount: number]: Layout | [] } = {};
        COUNTMAP[0] = [];
        COUNTMAP[1] = oneComponent;
        COUNTMAP[2] = twoComponent;
        COUNTMAP[3] = threeComponent;
        COUNTMAP[4] = fourComponent;
        COUNTMAP[5] = fiveComponent;

        const noOfComponents = this.ranks().length;

        return {
            layout: COUNTMAP[noOfComponents],
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        };
    },
    computed: {},
    methods: {
        ranks(this: any): Array<string> {
            const PRIORITY = ["Logs", "MLOps", "MQ", "Catalogue", "Meter"]
            const components = Object.keys(this.args)
            const ranks = PRIORITY.filter(value => components.includes(value));
            return ranks
        },

        retrieveUrl(this: any, name: string): string {
            const url = this.args[name];
            return url;
        },
    },
};

























export default {
    name: "MyComponent",
    props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
    components: {
        GridLayout,
        GridItem,
    },
    data(this: any) {
        const PRIORITY = ["Logs", "MLOps", "MQ", "Catalogue", "Meter"];
        const components = Object.keys(this.args);
        const ranks = PRIORITY.filter((value) => components.includes(value));

        const oneComponent = [{ x: 0, y: 0, w: 12, h: 12, i: "0" }];
        const twoComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
        ];
        const threeComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
            { x: 0, y: 0, w: 8, h: 18, i: "2" },
        ];
        const fourComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
            { x: 0, y: 0, w: 8, h: 18, i: "2" },
            { x: 0, y: 0, w: 8, h: 18, i: "3" },
        ];
        const fiveComponent = [
            { x: 0, y: 0, w: 8, h: 18, i: "0" },
            { x: 0, y: 0, w: 8, h: 18, i: "1" },
            { x: 0, y: 0, w: 8, h: 18, i: "2" },
            { x: 0, y: 0, w: 8, h: 18, i: "3" },
            { x: 0, y: 0, w: 8, h: 18, i: "4" },
        ];

        const COUNTMAP: { [componentCount: number]: Layout | [] } = {};
        COUNTMAP[0] = [];
        COUNTMAP[1] = oneComponent;
        COUNTMAP[2] = twoComponent;
        COUNTMAP[3] = threeComponent;
        COUNTMAP[4] = fourComponent;
        COUNTMAP[5] = fiveComponent;

        const noOfComponents = ranks.length;

        return {
            layout: COUNTMAP[noOfComponents],
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        };
    },
    computed: {},
    methods: {
        retrieveUrl(this: any, name: string): string {
            const url = this.args[name];
            return url;
        },
    },
};

















input[type="checkbox"] {
    display: none;
}
.label {
    border: 1px solid #000;
    display: inline-block;
    padding: 3px;
    /* background: url("unchecked.png") no-repeat left center;  */
    /* padding-left: 15px; */
}
input[type="checkbox"]:checked + .label {
    background: #f00;
    color: #fff;
    /* background-image: url("checked.png"); */
}

.vue-grid-layout {
    background: #eee;
}
.vue-grid-item:not(.vue-grid-placeholder) {
    background: #ccc;
    border: 1px solid black;
}
.vue-grid-item .resizing {
    opacity: 0.9;
}
.vue-grid-item .static {
    background: #cce;
}
.vue-grid-item .text {
    font-size: 24px;
    text-align: center;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
    height: 100%;
    width: 100%;
}
.vue-grid-item .no-drag {
    height: 100%;
    width: 100%;
}
.vue-grid-item .minMax {
    font-size: 12px;
}
.vue-grid-item .add {
    cursor: pointer;
}
.vue-draggable-handle {
    position: absolute;
    width: 20px;
    height: 20px;
    top: 0;
    left: 0;
    background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>")
        no-repeat;
    background-position: bottom right;
    padding: 0 8px 8px 0;
    background-repeat: no-repeat;
    background-origin: content-box;
    box-sizing: border-box;
    cursor: pointer;
}
.layoutJSON {
    background: #ddd;
    border: 1px solid black;
    margin-top: 10px;
    padding: 10px;
}
.columns {
    -moz-columns: 120px;
    -webkit-columns: 120px;
    columns: 120px;
}

#window {
    margin-top: 0.4rem;
    width: 100%;
    height: 100%;
    position: relative;
}

















        <span> Hello, {{ args }} {{ typeof args }}! </span>
        <!-- <span>{{ ranks }} {{ typeof ranks }} {{ typeof ranks[0] }}</span> -->
        <span>{{ layout }} {{ typeof layout }}</span>








                    :static="item.static"



// import { Streamlit } from "streamlit-component-lib";




            const threeComponent = [
                { x: 0, y: 0, w: 12, h: 9, i: 0 },
                { x: 0, y: 9, w: 6, h: 9, i: 1 },
                { x: 6, y: 9, w: 6, h: 9, i: 2 },
            ];













/* .label {
    border: 1px solid #000;
    display: inline-block;
    padding: 3px;
}
input[type="checkbox"]:checked + .label {
    background: #f00;
    color: #fff;
} */











/* #viewport {
    display: inline-block;
    flex-direction: column;
} */

/* #viewport div {
    flex-grow: 0;
    flex-shrink: 0;
} */



















<template>
    <div id="viewport">
        <div id="control-bar" class="container">
            <span id="checkbox">
                <input
                    id="checkbox-element"
                    type="checkbox"
                    v-model="draggable"
                />
                <i class="bi bi-arrows-move"></i>
            </span>
            <span id="checkbox">
                <input
                    id="checkbox-element"
                    type="checkbox"
                    v-model="resizable"
                />
                <i class="bi bi-aspect-ratio"></i>
            </span>
            <span id="checkbox">
                <input
                    id="checkbox-element"
                    type="checkbox"
                    v-model="responsive"
                />
                <i class="bi bi-grid-1x2"></i>
            </span>
        </div>
        <div id="command-station">
            <grid-layout
                :layout.sync="layout"
                :col-num="18"
                :row-height="35"
                :is-draggable="draggable"
                :is-resizable="resizable"
                :responsive="responsive"
                :vertical-compact="true"
                :use-css-transforms="true"
            >
                <grid-item
                    v-for="item in layout"
                    :x="item.x"
                    :y="item.y"
                    :w="item.w"
                    :h="item.h"
                    :i="item.i"
                    :key="item.i"
                >
                    <iframe
                        :src="retrieveUrl(ranks[item.i])"
                        id="window"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item>
            </grid-layout>
        </div>
    </div>
</template>


<script lang="ts">
import { GridLayout, GridItem } from "vue-grid-layout";

// Declare custom typings
type Window = {
    x: number;
    y: number;
    w: number;
    h: number;
    i: number;
};
type Layout = Array<Window>;

export default {
    name: "MyComponent",
    props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
    components: {
        GridLayout,
        GridItem,
    },
    data(this: any) {
        return {
            ranks: this.computeRanks(),
            layout: this.computeLayout(),
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        };
    },
    methods: {
        computeRanks(this: any): Array<string> {
            const PRIORITY = ["MQ", "Logs", "MLOps", "Catalogue", "Meter"];
            const components = Object.keys(this.args);
            const ranks = PRIORITY.filter((value) =>
                components.includes(value)
            );
            return ranks;
        },

        computeLayout() {
            const oneComponent = [{ x: 0, y: 0, w: 12, h: 18, i: 0 }];
            const twoComponent = [
                { x: 0, y: 0, w: 6, h: 18, i: 0 },
                { x: 6, y: 0, w: 6, h: 18, i: 1 },
            ];
            const threeComponent = [
                { x: 0, y: 0, w: 12, h: 9, i: 0 },
                { x: 0, y: 9, w: 6, h: 9, i: 1 },
                { x: 6, y: 9, w: 6, h: 9, i: 2 },
            ];
            const fourComponent = [
                { x: 0, y: 0, w: 6, h: 9, i: 0 },
                { x: 0, y: 9, w: 6, h: 9, i: 1 },
                { x: 6, y: 0, w: 6, h: 9, i: 2 },
                { x: 6, y: 9, w: 6, h: 9, i: 3 },
            ];
            const fiveComponent = [
                { x: 0, y: 0, w: 6, h: 9, i: 0 },
                { x: 6, y: 0, w: 6, h: 9, i: 1 },
                { x: 0, y: 9, w: 4, h: 9, i: 2 },
                { x: 4, y: 9, w: 4, h: 9, i: 3 },
                { x: 8, y: 9, w: 4, h: 9, i: 4 },
            ];

            const COUNTMAP: { [componentCount: number]: Layout | [] } = {};
            COUNTMAP[0] = [];
            COUNTMAP[1] = oneComponent;
            COUNTMAP[2] = twoComponent;
            COUNTMAP[3] = threeComponent;
            COUNTMAP[4] = fourComponent;
            COUNTMAP[5] = fiveComponent;

            const noOfComponents = this.computeRanks().length;

            return COUNTMAP[noOfComponents];
        },

        retrieveUrl(this: any, name: string): string {
            const url = this.args[name];
            return url;
        },
    },
};
</script>


<style scoped>
#viewport {
    width: 100%; 
    height: auto;
}

#control-bar {
    display: flex;
    flex-flow: column;
    /* text-align: right; */
    float: right;
    height: 100%;

}

#checkbox {
    background: #f5f5f5;
    display: block;
    padding: 10px 10px;
    border-radius: 2px;
    position: relative;
    cursor: pointer;
}

#checkbox-element {
    display: block;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    z-index: 99999;
    opacity: 0;
}

#checkbox > input[type="checkbox"] + i {
    color: black;
}

#checkbox > input[type="checkbox"]:checked + i {
    color: #da7f4d;
}

#command-station {
    width: calc(100% - 36px); 
    height: 100%;
    float: left;
}

.vue-grid-layout {
    background: #f5f5f5;
}
.vue-grid-item:not(.vue-grid-placeholder) {
    background: #ffffff;
    border: 1px solid black;
}
.vue-grid-item .resizing {
    opacity: 0.9;
}
.vue-grid-item .static {
    background: #cce;
}
.vue-grid-item .text {
    font-size: 24px;
    text-align: center;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
    height: 100%;
    width: 100%;
}
.vue-grid-item .no-drag {
    height: 100%;
    width: 100%;
}
.vue-grid-item .minMax {
    font-size: 12px;
}
.vue-grid-item .add {
    cursor: pointer;
}
.vue-draggable-handle {
    position: absolute;
    width: 20px;
    height: 20px;
    top: 0;
    left: 0;
    /* background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>")
        no-repeat; */
    background-position: bottom right;
    padding: 0 8px 8px 0;
    background-repeat: no-repeat;
    background-origin: content-box;
    box-sizing: border-box;
    cursor: pointer;
}
.layoutJSON {
    background: #ddd;
    border: 1px solid black;
    margin-top: 10px;
    padding: 10px;
}
.columns {
    -moz-columns: 120px;
    -webkit-columns: 120px;
    columns: 120px;
}

#window {
    width: 100%;
    height: 100%;
    position: relative;
}
</style>