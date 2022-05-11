#!/usr/bin/env bash

# Auto-detect & override default host with remote host 
export SYNUI_REMOTE_HOST=$(curl -s 'https://checkip.amazonaws.com')

# Start Synergos UI with remote settings
docker-compose --env-file settings.env up