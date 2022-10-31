import supervisely as sly
from supervisely.app.widgets import Card, Table, Container, SlyTqdm
import src.globals as g
import pandas as pd
import numpy as np
import open3d as o3d
from src.ui.utils import get_agg_stats
from supervisely import (
    PointcloudObject,
    PointcloudEpisodeAnnotation,
    PointcloudAnnotation,
    PointcloudEpisodeDataset,
    PointcloudDataset,
)

lines = None
cols = [
    "name",
    "id",
    "pointclouds count",
    "objects count",
    "average points count per pointcloud",
    "pointclouds without objects",
    "average size x",
    "average size y",
    "average size z",
    "average min x",
    "average max x",
    "average min y",
    "average max y",
    "average min z",
    "average max z",
]
cols = list(map(str.upper, cols))

progress = SlyTqdm()
progress.hide()
table = Table(fixed_cols=1, width="100%")
START_LOCK_MESSAGE = "Please wait..."

card = Card(
    "5️⃣ Datasets",
    collapsable=True,
    content=Container([progress, table], gap=0),
    lock_message=START_LOCK_MESSAGE,
)
card.lock()


def bold_text(text):
    def bold(t):
        return f"<b>{t}</b>"

    if isinstance(text, list):
        return [bold(t) for t in text]
    return bold(text)


def build_table(round_floats=4):
    global lines, table, cols, progress
    if lines is None:
        lines = []
    table.loading = True
    progress.show()
    cols.extend([obj_class.name for obj_class in g.project_meta.obj_classes])

    ds_infos = g.api.dataset.get_list(g.project_id)
    total_len_ptc = []
    total_num_objects = []
    total_ptc_len = []
    total_pcd_ranges = []
    total_pcd_sizes = []
    total_ptc_without_objs = []
    total_num_objects_class = []
    with progress(
        message=f"Calculating datasets stats...", total=len(g.project_fs.datasets)
    ) as pbar:
        for ds in g.project_fs.datasets:
            ds_id = None
            for ds_info in ds_infos:
                if ds_info.name == ds.name:
                    ds_id = ds_info.id
            num_objects = 0
            ptc_len = []
            pcd_ranges = []
            pcd_sizes = []
            ptc_without_objs = 0
            num_objects_class = {}
            for obj_class in g.project_meta.obj_classes:
                num_objects_class[obj_class.name] = 0
            for item_name in ds:
                paths = ds.get_item_paths(item_name)
                ptc_path = paths.pointcloud_path
                if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                    ds: PointcloudDataset
                    ann: PointcloudAnnotation = ds.get_ann(item_name, g.project_meta)
                    objs = ann.get_objects_from_figures()
                    num_objects += len(objs)
                    if not objs:
                        ptc_without_objs += 1

                elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                    ds: PointcloudEpisodeDataset
                    ann: PointcloudEpisodeAnnotation = ds.get_ann(g.project_meta)
                    frame_idx = ds.get_frame_idx(item_name)
                    objs = ann.get_objects_on_frame(frame_idx)
                    if not len(objs):
                        ptc_without_objs += 1
                    # Do it once for episodes
                    if not num_objects:
                        num_objects += len(ann.objects)

                for obj in objs:
                    obj: PointcloudObject
                    num_objects_class[obj.obj_class.name] += 1
                pcd = o3d.io.read_point_cloud(ptc_path)
                pcd_np = np.asarray(pcd.points)
                ptc_len.append(len(pcd_np))
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
                pcd_ranges.append(pcd_range)
                pcd_sizes.append(pcd_size)

            ptc_len = get_agg_stats(ptc_len, round_floats, "mean")
            pcd_ranges = get_agg_stats(pcd_ranges, round_floats, "mean")
            pcd_sizes = get_agg_stats(pcd_sizes, round_floats, "mean")

            lines.append(
                [
                    ds.name,
                    ds_id,
                    len(ds),
                    num_objects,
                    ptc_len,
                    ptc_without_objs,
                    *pcd_sizes,
                    *pcd_ranges,
                    *list(num_objects_class.values()),
                ]
            )

            total_len_ptc.append(len(ds))
            total_num_objects.append(num_objects)
            total_ptc_len.append(ptc_len)
            total_pcd_ranges.append(pcd_ranges)
            total_pcd_sizes.append(pcd_sizes)
            total_ptc_without_objs.append(ptc_without_objs)
            total_num_objects_class.append(list(num_objects_class.values()))
            pbar.update()

    total_len_ptc = sum(total_len_ptc)
    total_num_objects = sum(total_num_objects)
    total_ptc_len = get_agg_stats(total_ptc_len, round_floats, "mean")
    total_ptc_without_objs = sum(total_ptc_without_objs)
    total_pcd_sizes = get_agg_stats(total_pcd_sizes, round_floats, "mean")
    total_pcd_ranges = get_agg_stats(total_pcd_ranges, round_floats, "mean")
    total_num_objects_class = get_agg_stats(total_num_objects_class, round_floats, "sum")

    df = pd.DataFrame(lines, columns=cols)
    table.read_pandas(df)

    total_row = [
        bold_text("TOTAL"),
        "-",
        bold_text(total_len_ptc),
        bold_text(total_num_objects),
        bold_text(total_ptc_len),
        bold_text(total_ptc_without_objs),
        *bold_text(total_pcd_sizes),
        *bold_text(total_pcd_ranges),
        *bold_text(total_num_objects_class),
    ]
    table.summary_row = total_row
    table.loading = False
    progress.hide()
