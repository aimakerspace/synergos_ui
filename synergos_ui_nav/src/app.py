####################
# Required Modules #
####################

# Genric/Built-in
from pathlib import Path

# Libs
from flask import Flask, jsonify, request
from flask_cors import CORS
from synarchive.connection import (CollaborationRecords, ExperimentRecords,
                                   ProjectRecords, RunRecords)

# Custom
from .config import nav_config

##################
# Configurations #
##################
DEBUG = False
config = nav_config[nav_config['ENV']]

DB_PATH = Path(config['db']['path'])
collabs = CollaborationRecords(db_path=DB_PATH)
projects = ProjectRecords(db_path=DB_PATH)
expts = ExperimentRecords(db_path=DB_PATH)
runs = RunRecords(db_path=DB_PATH)

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

#############
# Functions #
#############

@app.route('/nav/ping', methods=['GET'])
def ping_pong():
    """Health check endpoint

    Returns:
        json: Positive response message
    """
    if DEBUG:
        app.logger.debug(collabs.read_all())
    return jsonify('connected!')


@app.route('/nav/collabs', methods=['GET'])
def nav_collabs():
    """Returns list of collaborations

    Returns:
        json: List of collaboration
    """
    response = {'status': "success"}

    collab_list = [{'name':c['key']['collab_id'].split('-')[0], 
                    'id':c['key']['collab_id']} 
                   for c in collabs.read_all()]

    response['results'] = {
        'collabs': collab_list
    }

    return jsonify(response)

@app.route('/nav/projects/', methods=['GET'])
def nav_projects():
    """Returns list of projects and optionally filter by collab id

    Returns:
        json: List of projects
    """

    response = {'status': "success"}
    project_list = None
        
    collab_id = request.args.get('collab_id')
    if collab_id:
        project_list = [{'name': c['key']['project_id'].split('-')[0], 
                         'id':c['key']['project_id'], 
                         'zzdebug': c['key']['collab_id']} 
                        for c in projects.read_all() 
                        if c['key']['collab_id'] == collab_id]
    else:
        project_list = [{'name': c['key']['project_id'].split('-')[0], 
                         'id':c['key']['project_id']} 
                        for c in projects.read_all()]
        
    response['results'] = {
            'projects': project_list
    }

    return jsonify(response)


@app.route('/nav/expts', methods=['GET'])
def nav_expts():
    """Returns list of experiments, optionally filtered by project id

    Returns:
        json: List of experiments
    """
    response = {'status': "success"}
    expt_list = None
        
    project_id = request.args.get('project_id')
    if project_id:
        expt_list = [{'name': c['key']['expt_id'].split('-')[0], 
                      'id':c['key']['expt_id'], 
                      'zzdebug': c['key']['project_id']} 
                     for c in expts.read_all() 
                     if c['key']['project_id'] == project_id]
    else:
        expt_list = [{'name': c['key']['expt_id'].split('-')[0], 
                      'id':c['key']['expt_id']}
                     for c in expts.read_all()]
        
    response['results'] = {
            'expts': expt_list
    }

    return jsonify(response)


@app.route('/nav/runs', methods=['GET'])
def all_runs():
    """Returns list of runs, optionally filtered by experiment id

    Returns:
        json: List of runs
    """
    response = {'status': "success"}
    run_list = None
        
    expt_id = request.args.get('expt_id')
    if expt_id:
        run_list = [{'name': c['key']['run_id'].split('-')[0], 
                     'id':c['key']['run_id'], 
                     'zzdebug': c['key']['expt_id']}
                    for c in runs.read_all() 
                    if c['key']['expt_id'] == expt_id]
    else:
        run_list = [{'name': c['key']['id'].split('-')[0], 
                     'id':c['key']['run_id']}
                    for c in runs.read_all()]
        
    response['results'] = {
            'runs': run_list
    }

    return jsonify(response)

@app.route('/nav/run_metadata', methods=['GET'])
def nav_run_metadata():
    """Returns config of each run and associated source list

    Returns:
        json: source list and run config
    """
    response = {'status': "success"}
    source_list = config['source_list']
    
    collab_id = request.args.get('collab_id')
    project_id = request.args.get('project_id')
    expt_id = request.args.get('expt_id')
    run_id = request.args.get('run_id')
    
    db_run_results = runs.read(collab_id=collab_id, 
                               project_id=project_id, 
                               expt_id=expt_id, 
                               run_id=run_id)
    
    if db_run_results:
        db_run_results.pop('relations') # trimming results
        run_key = db_run_results.pop('key')
        for k, v in run_key.items():
            db_run_results[k] = v
    else:
        db_run_results = {}
        
    response['results'] = {
            'sources': source_list,
            'config': db_run_results,
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(host=config['app']['host'], port=config['app']['port'])
