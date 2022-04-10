#!/usr/bin/env bash

export FLASK_APP=app_auth
export FLASK_DEBUG=1
python -m flask run --cert=cert.pem --key=key.pem

