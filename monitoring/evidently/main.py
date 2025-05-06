############################
# Auteur :  Heuze Florent (contact@heuzef.com)
# Date : 06/2025
# Description : Drift Monitoring

# Import lib ###############

import os
from datetime import datetime
import time
import json
import shutil
import numpy as np
import pandas as pd
import logging
import requests
import evidently
from evidently.metrics import RegressionQualityMetric, RegressionErrorPlot, RegressionErrorDistribution
from evidently.metric_preset import DataDriftPreset, RegressionPreset, TargetDriftPreset
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.report import Report
from evidently.ui.workspace import Workspace

# ignore warnings
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

############################
# FUNCTIONS

############################
# MAIN SCRIPT

if __name__ == "__main__":
    
    # Define constants for project
    workspace_name = "workspace"
    project_name = "parivision"
    project_description = "Drift monitoring for PariVision"
    data = "./file.csv"
    target = "target"
    prediction = "prediction"

    # Clean olds reports
    # shutil.rmtree("html")
    # shutil.rmtree(workspace_name)
    # os.makedirs("html")
    # workspace = Workspace.create(workspace_name)
    # project = workspace.create_project(project_name)
    # project.description = project_description

    # Define column mapping
    column_mapping = ColumnMapping()
    column_mapping.target = target
    column_mapping.prediction = prediction

    # Ingest data
    # ...

    # Drift analyse
    # target_drift_report = Report(metrics=[TargetDriftPreset()])
    # data_drift_report.run(reference_data=ref_data.sort_index(), current_data=cur_data.sort_index(), column_mapping=column_mapping)
    # data_drift_report.save_html("./html/data_drift_report.html")
    # workspace.add_report(project.id, data_drift_report)

    print("workspace_name : ", workspace_name)
    print("project_name : ", project_name)
    print("project_description : ", project_description)
    print("data : ", data)
    print("target : ", target)
    print("prediction : ", prediction)
    print("column_mapping : ", column_mapping)