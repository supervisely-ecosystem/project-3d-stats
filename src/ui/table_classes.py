import supervisely as sly
from supervisely.app.widgets import Card, Table, Container, SlyTqdm, Checkbox
import src.globals as g
import pandas as pd
import numpy as np
from supervisely.video_annotation.key_id_map import KeyIdMap
from supervisely.geometry.cuboid_3d import Cuboid3d
from src.ui.utils import get_agg_stats

lines = None
cols = [
    "name",
    "geometry",
    "poinclouds count",
    "objects count",
    "figures count",
    "average object volume",
    "average objects count per pointcloud",
    "average size x",
    "average size y",
    "average size z",
    "position x min",
    "position x max",
    "position y min",
    "position y max",
    "position z min",
    "position z max",
]
cols = list(map(str.upper, cols))

progress = SlyTqdm()
progress.hide()
table = Table(fixed_cols=1, width="100%")
START_LOCK_MESSAGE = "Please wait..."

card = Card(
    "3️⃣ Classes",
    collapsable=True,
    content=Container([progress, table]),
    lock_message=START_LOCK_MESSAGE,
)
card.lock()


def build_table(round_floats=4):
    global lines, table, cols, progress
    if lines is None:
        lines = []
    table.loading = True
    progress.show()
    class_stats = {}

    for obj_class in g.project_meta.obj_classes:
        class_stats[obj_class.name] = {}
        class_stats[obj_class.name]["poinclouds count"] = 0
        class_stats[obj_class.name]["objects count"] = 0
        class_stats[obj_class.name]["figures count"] = 0
        class_stats[obj_class.name]["object volume"] = []
        class_stats[obj_class.name]["objects count per pointcloud"] = []
        class_stats[obj_class.name]["size x"] = []
        class_stats[obj_class.name]["size y"] = []
        class_stats[obj_class.name]["size z"] = []
        class_stats[obj_class.name]["position x"] = []
        class_stats[obj_class.name]["position y"] = []
        class_stats[obj_class.name]["position z"] = []

    pbar = progress(message=f"Calculating classes stats...", total=g.project_fs.total_items)
    for ds in g.project_fs.datasets:
        if g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
            ann_path = ds.get_ann_path()
            ann_json = sly.json.load_json_file(ann_path)
            ann = sly.PointcloudEpisodeAnnotation.from_json(ann_json, g.project_meta)
            frame_ptc_map_path = ds.get_frame_pointcloud_map_path()
            frame_ptc_map = sly.json.load_json_file(frame_ptc_map_path)
            ptc_frame_map = {v: k for k, v in frame_ptc_map.items()}

        for item_name in ds:
            if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                paths = ds.get_item_paths(item_name)
                ann_path = paths.ann_path
                ann_json = sly.json.load_json_file(ann_path)
                ann = sly.PointcloudAnnotation.from_json(ann_json, g.project_meta)
                ann_objects = {}
                for fig in ann.figures:
                    if fig.parent_object.key() not in ann_objects.keys():
                        ann_objects[fig.parent_object.key()] = fig.parent_object
                objs = ann_objects.values()
                figs = ann.figures

            elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                current_frame = ann.frames.get(int(ptc_frame_map[item_name]), None)
                if current_frame is None:
                    objs = []
                    figs = []
                else:
                    frame_objects = {}
                    for fig in current_frame.figures:
                        if fig.parent_object.key() not in frame_objects.keys():
                            frame_objects[fig.parent_object.key()] = fig.parent_object
                    objs = frame_objects.values()
                    figs = current_frame.figures

            num_objects_class = {}
            num_figures_class = {}
            for obj_class in g.project_meta.obj_classes:
                num_objects_class[obj_class.name] = 0
                num_figures_class[obj_class.name] = 0
            for obj in objs:
                num_objects_class[obj.obj_class.name] += 1
            for fig in figs:
                class_name = fig.parent_object.obj_class.name
                num_figures_class[class_name] += 1
                if not isinstance(fig.geometry, Cuboid3d):
                    continue
                class_stats[class_name]["position x"].append(fig.geometry.position.x)
                class_stats[class_name]["position y"].append(fig.geometry.position.y)
                class_stats[class_name]["position z"].append(fig.geometry.position.z)
                class_stats[class_name]["size x"].append(fig.geometry.dimensions.x)
                class_stats[class_name]["size y"].append(fig.geometry.dimensions.y)
                class_stats[class_name]["size z"].append(fig.geometry.dimensions.z)
                class_stats[class_name]["object volume"].append(
                    fig.geometry.dimensions.x
                    * fig.geometry.dimensions.y
                    * fig.geometry.dimensions.z
                )
            for obj_class in g.project_meta.obj_classes:
                class_stats[obj_class.name]["objects count per pointcloud"].append(
                    num_objects_class[obj_class.name]
                )
                class_stats[obj_class.name]["objects count"] += num_objects_class[obj_class.name]
                class_stats[obj_class.name]["figures count"] += num_figures_class[obj_class.name]

                if num_objects_class[obj_class.name] != 0:
                    class_stats[obj_class.name]["poinclouds count"] += 1
            pbar.update()

    for obj_class in g.project_meta.obj_classes:
        class_stats[obj_class.name]["average object volume"] = get_agg_stats(
            class_stats[obj_class.name]["object volume"], round_floats, "mean"
        )
        class_stats[obj_class.name]["average objects count per pointcloud"] = get_agg_stats(
            class_stats[obj_class.name]["objects count per pointcloud"], round_floats, "mean"
        )
        class_stats[obj_class.name]["average size x"] = get_agg_stats(
            class_stats[obj_class.name]["size x"], round_floats, "mean"
        )
        class_stats[obj_class.name]["average size y"] = get_agg_stats(
            class_stats[obj_class.name]["size y"], round_floats, "mean"
        )
        class_stats[obj_class.name]["average size z"] = get_agg_stats(
            class_stats[obj_class.name]["size z"], round_floats, "mean"
        )
        class_stats[obj_class.name]["position x min"] = get_agg_stats(
            class_stats[obj_class.name]["position x"], round_floats, "min"
        )
        class_stats[obj_class.name]["position x max"] = get_agg_stats(
            class_stats[obj_class.name]["position x"], round_floats, "max"
        )
        class_stats[obj_class.name]["position y min"] = get_agg_stats(
            class_stats[obj_class.name]["position y"], round_floats, "min"
        )
        class_stats[obj_class.name]["position y max"] = get_agg_stats(
            class_stats[obj_class.name]["position y"], round_floats, "max"
        )
        class_stats[obj_class.name]["position z min"] = get_agg_stats(
            class_stats[obj_class.name]["position z"], round_floats, "min"
        )
        class_stats[obj_class.name]["position z max"] = get_agg_stats(
            class_stats[obj_class.name]["position z"], round_floats, "max"
        )
        lines.append(
            [
                obj_class.name,
                obj_class.geometry_type.geometry_name(),
                class_stats[obj_class.name]["poinclouds count"],
                class_stats[obj_class.name]["objects count"],
                class_stats[obj_class.name]["figures count"],
                class_stats[obj_class.name]["average object volume"],
                class_stats[obj_class.name]["average objects count per pointcloud"],
                class_stats[obj_class.name]["average size x"],
                class_stats[obj_class.name]["average size y"],
                class_stats[obj_class.name]["average size z"],
                class_stats[obj_class.name]["position x min"],
                class_stats[obj_class.name]["position x max"],
                class_stats[obj_class.name]["position y min"],
                class_stats[obj_class.name]["position y max"],
                class_stats[obj_class.name]["position z min"],
                class_stats[obj_class.name]["position z max"],
            ]
        )

    pbar.clear()
    df = pd.DataFrame(lines, columns=cols)
    table.read_pandas(df)
    table.loading = False
    progress.hide()
