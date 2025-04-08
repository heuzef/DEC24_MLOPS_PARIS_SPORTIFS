#!/bin/bash
cd /home/parivision/DEC24_MLOPS_PARIS_SPORTIFS
source .venv/bin/activate
bentoml build
bentoml list
bentoml containerize champion_service:latest