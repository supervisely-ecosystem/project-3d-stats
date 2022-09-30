import supervisely as sly
from supervisely.app.widgets import Card, ProjectThumbnail
import src.globals as g

card = Card(
    "1️⃣ Input Project",
    "Select project to show stats",
    collapsable=True,
    content=ProjectThumbnail(g.project_info)
)