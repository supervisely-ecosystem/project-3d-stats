import supervisely as sly
from supervisely.app.widgets import Card, Table
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

table = Table(fixed_cols=1, width="100%")
START_LOCK_MESSAGE = "Please wait..."

card = Card(
    "2️⃣ Pointclouds",
    collapsable=True,
    content=table,
    lock_message=START_LOCK_MESSAGE,
)
card.lock()
# 3️⃣


def build_table(progress, round_floats=4):
    global lines, table, cols
    if lines is None:
        lines = []
    table.loading = True
    cols.extend([obj_class.name for obj_class in g.project_meta.obj_classes])
    with progress(
        message=f"Calculating pointcloud stats...", total=g.project_fs.total_items
    ) as pbar:
        ds_infos = g.api.dataset.get_list(g.project_id)
        for ds in g.project_fs.datasets:
            ds_id = None
            for ds_info in ds_infos:
                if ds_info.name == ds.name:
                    ds_id = ds_info.id
            if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                ptc_infos = g.api.pointcloud.get_list(ds_id)
            elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                ptc_infos = g.api.pointcloud_episode.get_list(ds_id)
                ann_path = ds.get_ann_path()
                ann_json = sly.json.load_json_file(ann_path)
                ann = sly.PointcloudEpisodeAnnotation.from_json(ann_json, g.project_meta)
                frame_ptc_map_path = ds.get_frame_pointcloud_map_path()
                frame_ptc_map = sly.json.load_json_file(frame_ptc_map_path)
                ptc_frame_map = {v: k for k, v in frame_ptc_map.items()}
            for item in ptc_infos:
                if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                    paths = ds.get_item_paths(item.name)
                    ptc_path = paths.pointcloud_path
                    ann_path = paths.ann_path
                    ann_json = sly.json.load_json_file(ann_path)
                    ann = sly.PointcloudAnnotation.from_json(ann_json, g.project_meta, KeyIdMap())
                    num_objects = len(ann.objects)
                    num_objects_class = {}
                    for obj_class in g.project_meta.obj_classes:
                        num_objects_class[obj_class.name] = 0
                    for obj in ann.objects:
                        num_objects_class[obj.obj_class.name] += 1

                    labeling_url = sly.pointcloud.get_labeling_tool_url(ds_id, item.id)
                    labeling_tool_link = sly.pointcloud.get_labeling_tool_link(
                        labeling_url, item.name
                    )
                elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                    paths = ds.get_item_paths(item.name)
                    ptc_path = paths.pointcloud_path
                    labeling_url = sly.pointcloud_episodes.get_labeling_tool_url(ds_id, item.id)
                    labeling_tool_link = sly.pointcloud_episodes.get_labeling_tool_link(
                        labeling_url, item.name
                    )
                    current_frame = ann.frames.get(int(ptc_frame_map[item.name]))
                    frame_objects = {}
                    for fig in current_frame.figures:
                        if fig.parent_object.key() not in frame_objects.keys():
                            frame_objects[fig.parent_object.key()] = fig.parent_object
                    num_objects = len(frame_objects)
                    num_objects_class = {}
                    for obj_class in g.project_meta.obj_classes:
                        num_objects_class[obj_class.name] = 0
                    for obj in frame_objects.values():
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
                        item.id,
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

    df = pd.DataFrame(lines, columns=cols)
    table.read_pandas(df)
    table.loading = False
