#!/usr/bin/env bash

docker image build . -t=auth_app
docker run -dp 80:80 flask_auth
