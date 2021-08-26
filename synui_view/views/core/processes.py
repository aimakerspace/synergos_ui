#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Any, Union

# Libs


# Custom
from config import TMP_DIR
from synergos import Driver

##################
# Configurations #
##################


#########################################
# Custom Tracker class - TrackedProcess #
#########################################

class TrackedProcess:
    """ 
    Tracking class to help manage asynchronous requests for the same model
    and validation resources within a federated cycle. Only one party is
    allowed to trigger the intended process, while subsequent queries will
    get blocked until job has completed. This is done by tracking the existence
    of a tempfile that is generated upon process startup.

    Attributes:
        __STATUS (list(str)):
        extension (str): File extension/format of the generated tempfile
        connector (str): Connecting symbol for internal string constructions
        driver (Driver): Synergos abstraction object to facilitate REST operations
        p_type (str): Process type to be tracked in the context of the FL cycle
        filters (dict): Composite key of hierarchical IDs uniquely identifying
            the specified FL cycle to be tracked
    """
    def __init__(
        self, 
        driver: Driver, 
        p_type: str,
        filters: Dict[str, str],
        connector: str = "_-_",
        extension: str = "txt"
    ) -> Dict[str, str]:
        self.__STATUSES = ["Idle", "In-progress", "Completed"]
        self.extension = extension
        self.connector = connector
        self.driver = driver
        self.p_type = p_type
        self.filters = filters

    ###########
    # Getters #
    ###########

    @property
    def statuses(self):
        return self.__STATUSES


    def is_idle(self) -> bool:
        """ Checks if the job corresponding to the current keyset is 
            unattempted. A process is considered as idle if no tempfile is
            detected and no model is pulled from REST-RPC for the current set
            of filters (i.e. completed).

        Returns:
            Idling state (bool)
        """
        tmp_file = self.generate_tracking_path()
        is_started = os.path.isfile(tmp_file)
        return not is_started and not self.is_completed()


    def is_running(self) -> bool:
        """ Checks if the job corresponding to the current keyset is 
            still in progress. A process is considered as in progress if a 
            tempfile is detected, but no model corresponding to the current set
            of filters is available from REST-RPC.

        Returns:
            Idling state (bool)
        """
        tmp_file = self.generate_tracking_path()
        is_started = os.path.isfile(tmp_file)
        return is_started and not self.is_completed()


    def is_completed(self) -> bool:
        """ Checks if the job corresponding to the current keyset is 
            completed. A process is considered as completed if a model 
            corresponding to the current set of filters is accessible 
            from REST-RPC.

        Returns:
            Completed state (bool)
        """
        model_data = self.driver.models.read(**self.filters).get('data', {})
        valid_stats = self.driver.validations.read(**self.filters).get('data', {})
        return (bool(model_data) and bool(valid_stats))

    ###########
    # Helpers #
    ###########

    def format_timestamp(self, timestamp: datetime) -> str:
        return timestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")


    def generate_tracking_id(self) -> str:
        """ Generates a unique tracking ID for the specified set of filters
        
        Returns:
            Tracking ID (str)
        """
        collab_id = self.filters.get('collab_id', "")
        project_id = self.filters.get('project_id', "")
        expt_id = self.filters.get('expt_id', "")
        run_id = self.filters.get('run_id', "")
        return self.connector.join([collab_id, project_id, expt_id, run_id])


    def generate_tracking_path(self) -> str:
        """ Generates path to tempfile. 
            Note: This does not generate the file yet!
        
        Returns:
            Tracking path (str)
        """
        track_id = self.generate_tracking_id()
        tmp_name = f"{track_id}.{self.extension}"
        tmp_path = os.path.join(TMP_DIR, self.p_type, tmp_name)
        return tmp_path


    def create_tmpfile(self) -> str:
        """ Creates a physical/persistent tempfile to track the commencement
            of any requests under the specified keyset to REST-RPC 

        Returns:
            Tempfile path (str)
        """
        tmp_path = self.generate_tracking_path()
        Path(tmp_path).parent.absolute().mkdir(parents=True, exist_ok=True)

        # Create an empty file
        with open(tmp_path, 'w') as fp:
            pass

        return tmp_path


    def delete_tmpfile(self) -> str:
        """ Removes unique tempfile previously generated as post-process cleanup.

        Returns:
            Tempfile path (str)
        """
        try:
            tmp_path = self.generate_tracking_path()
            os.remove(tmp_path)
            return tmp_path
        except OSError as e:
            raise RuntimeError(f"Tempfile {tmp_path} does not exist! Error - {e}")
            

    def track_access(self) -> str:
        """ Tracks access attempts by storing timestamps in an already existing
            tempfile.

        Returns:
            Formatted datetime str (str)
        """
        tmp_path = self.generate_tracking_path()
        
        if os.path.isfile(tmp_path):
            with open(tmp_path, 'a') as tmp:
                time_accessed = self.format_timestamp(datetime.now())
                tmp.write(f"{time_accessed}\n")
            
            return time_accessed

        else:
            raise RuntimeError("Tempfile not detected! Process has to be started first before tracking.")


    def retrieve_start_time(self) -> str:
        """ Retrieves the starting time of tracked experiment

        Returns:
            Formatted start time (str)
        """
        tmp_path = self.generate_tracking_path()
        
        if os.path.isfile(tmp_path):
            with open(tmp_path, 'r') as tmp:
                start_time = tmp.readline().strip()
            
            return start_time

        else:
            raise RuntimeError("Tempfile not detected! Process has to be started first before tracking.")


    def retrieve_access_counts(self) -> str:
        """ Counts number of times process was viewed 
        """
        tmp_path = self.generate_tracking_path()

        if os.path.isfile(tmp_path):
            with open(tmp_path, 'r') as tmp:
                access_entries = tmp.readlines()

            return len(access_entries)

        else:
            raise RuntimeError("Tempfile not detected! Process has to be started first before tracking.")



    ##################
    # Core functions #
    ##################

    def start(self) -> str:
        """ Commences tracking of the remote process

        Returns:
            Formatted start time (str)
        """
        self.create_tmpfile()
        self.track_access()
        return self.retrieve_start_time()
    

    def stop(self) -> str:
        """ Terminates tracking of the remote process.
            Note: This does not stop the actual process!
        
        Returns:
            Time ended (str)
        """
        self.delete_tmpfile()
        return self.format_timestamp(datetime.now())


    def check(self) -> str:
        """ Determines status of the launched process corresponding to a specified
            federated keyset. There are 3 possible states:

            1. Idle       - Federated Job is unattempted 
            2. In-progess - Federated job is still in progress 
            3. Completed  - Federated job is completed
        """
        if self.is_idle():
            return self.statuses[0]
        elif self.is_running():
            return self.statuses[1]
        elif self.is_completed():
            return self.statuses[2]
        else:
            raise RuntimeError("Request was made during transition. Please try again.")



###########################################
# Custom Tracker class - TrackedInference #
###########################################

class TrackedInference(TrackedProcess):
    """ 
    Tracking class to help manage asynchronous requests for the same prediction
    resources, to be performed by the participant. Participants are only allowed
    to trigger the intended process ONCE, while subsequent participant queries
    to the same job will get blocked until job has completed. The tracking 
    mechanism is similar to its parent class (i.e. via means of a tempfile)

    Attributes:
        __STATUS (list(str)):
        extension (str): File extension/format of the generated tempfile
        connector (str): Connecting symbol for internal string constructions
        driver (Driver): Synergos abstraction object to facilitate REST operations
        p_type (str): Process type to be tracked in the context of the FL cycle
        filters (dict): Composite key of hierarchical IDs uniquely identifying
            the specified FL cycle to be tracked
    """
    def __init__(
        self, 
        driver: Driver,
        participant_id: str,
        filters: Dict[str, str],
        connector: str = "_-_",
        extension: str = "txt"
    ) -> Dict[str, str]:
        super().__init__(
            driver=driver,
            p_type="inference",
            filters=filters,
            connector=connector,
            extension=extension
        )
        self.participant_id = participant_id

    ###########
    # Getters #
    ###########

    def is_idle(self) -> bool:
        """ Checks if the job corresponding to the current keyset is 
            unattempted. An inference rocess is considered as idle if no 
            tempfile is detected and no inference results are pulled from 
            REST-RPC for the current set of filters (i.e. completed).

        Returns:
            Idling state (bool)
        """
        tmp_file = self.generate_tracking_path()
        is_started = os.path.isfile(tmp_file)
        return not is_started and not self.is_completed()


    def is_running(self) -> bool:
        """ Checks if the job corresponding to the current keyset is 
            still in progress. An inference process is considered as in 
            progress if a tempfile is detected. Unlike its parent, since 
            inference archives are overwritable, there is no need to check if
            it already exists.

        Returns:
            Idling state (bool)
        """
        tmp_file = self.generate_tracking_path()
        is_started = os.path.isfile(tmp_file)
        return is_started


    def is_completed(self) -> bool:
        """ Checks if the job corresponding to the current keyset is 
            completed. An inference process is considered as completed if the
            predictions corresponding to the current set of filters is 
            accessible from REST-RPC.

        Returns:
            Completed state (bool)
        """
        pred_stats = self.driver.predictions.read(
            participant_id=self.participant_id,
            **self.filters
        ).get('data', {})
        return bool(pred_stats)

    ###########
    # Helpers #
    ###########

    def generate_tracking_id(self) -> str:
        """ Generates a unique tracking ID for the specified set of filters
        
        Returns:
            Tracking ID (str)
        """
        process_tracking_id = super().generate_tracking_id()
        return self.connector.join([self.participant_id, process_tracking_id])