import supervisely as sly
from supervisely.app.widgets import Card, Table, Container, SlyTqdm
import src.globals as g
import pandas as pd
import numpy as np
import open3d as o3d
from supervisely import (
    PointcloudObject,
    PointcloudDataset,
    PointcloudEpisodeDataset,
    PointcloudEpisodeAnnotation,
    PointcloudAnnotation,
)

lines = None
cols = [
    "id",
    "link",
    "dataset",
    "points count",
    "objects count",
    "related images count",
    "tags",
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
    with progress(
        message="Calculating pointcloud stats...",
        total=g.project_info.items_count,
    ) as pbar:
        ds_infos = g.api.dataset.get_list(g.project_id)
        for ds in g.project_fs.datasets:
            ds_id = None
            for ds_info in ds_infos:
                if ds_info.name == ds.name:
                    ds_id = ds_info.id
            for item_name in ds:
                paths = ds.get_item_paths(item_name)
                ptc_path = paths.pointcloud_path
                item_info = ds.get_pointcloud_info(item_name)
                rel_images = ds.get_related_images(item_name)
                if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                    ds: PointcloudDataset
                    ann: PointcloudAnnotation = ds.get_ann(item_name, g.project_meta)
                    objs = ann.get_objects_from_figures()
                    tags = ann.tags

                    labeling_url = sly.pointcloud.get_labeling_tool_url(ds_id, item_info.id)
                    labeling_tool_link = sly.pointcloud.get_labeling_tool_link(
                        labeling_url, item_name
                    )
                elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                    ds: PointcloudEpisodeDataset
                    ann: PointcloudEpisodeAnnotation = ds.get_ann(g.project_meta)
                    frame_idx = ds.get_frame_idx(item_name)
                    objs = ann.get_objects_on_frame(frame_idx)
                    tags = ann.get_tags_on_frame(frame_idx)

                    labeling_url = sly.pointcloud_episodes.get_labeling_tool_url(
                        ds_id, item_info.id
                    )
                    labeling_tool_link = sly.pointcloud_episodes.get_labeling_tool_link(
                        labeling_url, item_name
                    )

                tag_names = ""
                for tag in tags:
                    name_type_val = tag.get_row_ptable()
                    tag_names += f"{name_type_val[0]}{':'+name_type_val[2] if name_type_val[2] is not None else ''},"
                if tag_names != "":
                    tag_names = tag_names[:-1]
                else:
                    tag_names = "-"
                num_objects = len(objs)
                num_objects_class = {}
                for obj_class in g.project_meta.obj_classes:
                    num_objects_class[obj_class.name] = 0
                for obj in objs:
                    obj: PointcloudObject
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
                        len(rel_images),
                        tag_names,
                        *pcd_size,
                        *pcd_range,
                        *list(num_objects_class.values()),
                    ]
                )
                pbar.update()
    df = pd.DataFrame(lines, columns=cols)
    table.read_pandas(df)
    table.loading = False
    progress.hide()
