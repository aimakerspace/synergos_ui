#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Custom


##################
# Configurations #
##################

# app = Flask(__name__, static_url_path='/static')
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

####################################
# Navigation UI - Supported Routes #
#################################### 

@app.get("/", response_class=HTMLResponse)
def load_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
def load_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/orchestrator", response_class=HTMLResponse)
def load_orchestrator(request: Request):
    return templates.TemplateResponse("orchestrator.html", {"request": request})


@app.get("/participant", response_class=HTMLResponse)
def load_participant(request: Request):
    return templates.TemplateResponse("participant.html", {"request": request})


@app.get("/actions/{role}/{resource}", response_class=HTMLResponse)
def load_actions(request: Request, role: str, resource: str):
    return templates.TemplateResponse(
        "actions.html", 
        {"request": request, 'role': role, 'resource': resource}
    )


@app.get("/view/{role}/{resource}/{action}", response_class=HTMLResponse)
def load_view(request: Request, role: str, resource: str, action: str):
    return templates.TemplateResponse(
        "viewport.html",
        {
            'request': request, 
            'role': role, 
            'resource': resource, 
            'action': action
        }
    )