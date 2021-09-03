# Synergos UI

Unified UI component of a Synergos network

## Pre-reqs

### Components
- Run the following components so that they can be displayed
  - mlflow
  - rabbitmq
  - graylog
  - amundsen
  - neo4j-browser
- For mlflow, you can refer to the `Dockerfile-mlflow.dev` file for reference
  - To launch this container, run the following commands:
    - `docker build -f Dockerfile-mlflow.dev -t mlflow-docker:dev .`
    - `docker run -it --rm -p 15000:5000 -v /path/to/run/mlflow_test/test_project:/tmp/project mlflow-docker:dev`
- For neo4j-browser, you can reference the file `Dockerfile-neo4j-browser.dev`
  - To launch this container, run the following commands:
    - `docker build -f Dockerfile-neo4j-browser.dev -t neo4j-browser-docker:dev .`
    - `docker run -it --rm -p 7400:8080 neo4j-browser-docker:dev`

### Component UI paths
- Update the component URLs inside the `source_list` option in `synergos_ui_nav/src/config.py`

## Instructions to run UI component
- Run the following command: `docker-compose -f docker-compose-dev.yml up --build`
- Go to `http://localhost` to visit the page in the browser

## Dev notes
- mlflow needs to be run behind the nginx reverse proxy, else there will be CORS issues
- The UI Frontend (Vue 3 based) and Backend (Python based) are also run behind the ngnix reverse proxy
- Please note that direct app URLs need to be used for the following components
  - rabbitmq
  - graylog
  - amundsen
  - neo4j-browser
