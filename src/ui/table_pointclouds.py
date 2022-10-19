import supervisely as sly
from supervisely.app.widgets import Card, Table, Container, SlyTqdm
import src.globals as g
import pandas as pd
import numpy as np
import open3d as o3d
from supervisely.video_annotation.key_id_map import KeyIdMap

lines = None
cols = [
    "id",
    "link",
    "dataset",
    "points count",
    "objects count",
    "size x",
    "size y",
    "size z",
    "min x",
    "max x",
    "min y",
    "max y",
    "min z",
    "max z",
]
cols = list(map(str.upper, cols))
progress = SlyTqdm()
table = Table(fixed_cols=1, width="100%")
START_LOCK_MESSAGE = "Please wait..."

card = Card(
    "2️⃣ Pointclouds",
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
    cols.extend([obj_class.name for obj_class in g.project_meta.obj_classes])
    pbar = progress(
        message=f"Calculating pointcloud stats...",
        total=g.project_info.items_count,
    )
    ds_infos = g.api.dataset.get_list(g.project_id)
    for ds in g.project_fs.datasets:
        ds_id = None
        for ds_info in ds_infos:
            if ds_info.name == ds.name:
                ds_id = ds_info.id
        if g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
            ann_path = ds.get_ann_path()
            ann_json = sly.json.load_json_file(ann_path)
            ann = sly.PointcloudEpisodeAnnotation.from_json(ann_json, g.project_meta)
            frame_ptc_map_path = ds.get_frame_pointcloud_map_path()
            frame_ptc_map = sly.json.load_json_file(frame_ptc_map_path)
            ptc_frame_map = {v: k for k, v in frame_ptc_map.items()}
        for item_name in ds:
            paths = ds.get_item_paths(item_name)
            ptc_path = paths.pointcloud_path
            item_info = ds.get_pointcloud_info(item_name)
            if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                ann_path = paths.ann_path
                # TODO: calculate related images
                ann_json = sly.json.load_json_file(ann_path)
                ann = sly.PointcloudAnnotation.from_json(ann_json, g.project_meta)
                ann_objects = {}
                # TODO: maybe fix objects in PointcloudAnnotation?
                for fig in ann.figures:
                    if fig.parent_object.key() not in ann_objects.keys():
                        ann_objects[fig.parent_object.key()] = fig.parent_object
                num_objects = len(ann_objects)
                objs = ann_objects.values()

                labeling_url = sly.pointcloud.get_labeling_tool_url(ds_id, item_info.id)
                labeling_tool_link = sly.pointcloud.get_labeling_tool_link(labeling_url, item_name)
            elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                labeling_url = sly.pointcloud_episodes.get_labeling_tool_url(ds_id, item_info.id)
                labeling_tool_link = sly.pointcloud_episodes.get_labeling_tool_link(
                    labeling_url, item_name
                )
                current_frame = ann.frames.get(int(ptc_frame_map[item_name]), None)
                if current_frame is None:
                    num_objects = 0
                    objs = []
                else:
                    frame_objects = {}
                    for fig in current_frame.figures:
                        if fig.parent_object.key() not in frame_objects.keys():
                            frame_objects[fig.parent_object.key()] = fig.parent_object
                    num_objects = len(frame_objects)
                    objs = frame_objects.values()

            num_objects_class = {}
            for obj_class in g.project_meta.obj_classes:
                num_objects_class[obj_class.name] = 0
            for obj in objs:
                num_objects_class[obj.obj_class.name] += 1

            pcd = o3d.io.read_point_cloud(ptc_path)
            pcd_np = np.asarray(pcd.points)
            pcd_range = [
                round(pcd_np[:, 0].min(), round_floats),
                round(pcd_np[:, 0].max(), round_floats),
                round(pcd_np[:, 1].min(), round_floats),
                round(pcd_np[:, 1].max(), round_floats),
                round(pcd_np[:, 2].min(), round_floats),
                round(pcd_np[:, 2].max(), round_floats),
            ]
            pcd_size = [
                round(pcd_range[1] - pcd_range[0], round_floats),
                round(pcd_range[3] - pcd_range[2], round_floats),
                round(pcd_range[5] - pcd_range[4], round_floats),
            ]
            lines.append(
                [
                    item_info.id,
                    labeling_tool_link,
                    ds_id,
                    len(pcd_np),
                    num_objects,
                    *pcd_size,
                    *pcd_range,
                    *list(num_objects_class.values()),
                ]
            )
            pbar.update()
    pbar.clear()
    df = pd.DataFrame(lines, columns=cols)
    table.read_pandas(df)
    table.loading = False
    progress.hide()
