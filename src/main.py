import os
from dotenv import load_dotenv

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

import supervisely as sly
from supervisely.app.widgets import Container
import src.ui.input_project as input_project
import src.ui.table_pointclouds as pointclouds


settings = Container([input_project.card, pointclouds.card])

app = sly.Application(layout=settings)
