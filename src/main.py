import os
from dotenv import load_dotenv

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

import supervisely as sly
from supervisely.app.widgets import Card, Container, VideoThumbnail
import src.globals as g
import src.ui.input_project as input_project


settings = Container(
    [input_project.card]
)

app = sly.Application(layout=settings)
