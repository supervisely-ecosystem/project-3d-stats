import os
from dotenv import load_dotenv

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

import supervisely as sly
from supervisely.app.widgets import Container
import src.ui.input_project as input_project
import src.ui.table_pointclouds as pointclouds
import src.ui.table_classes as classes
import src.ui.table_labels as labels
import src.ui.table_datasets as datasets

settings = Container(
    [input_project.card, pointclouds.card, classes.card, labels.card, datasets.card]
)

app = sly.Application(layout=settings)
