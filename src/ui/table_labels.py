import supervisely as sly
from supervisely.app.widgets import Card, Table, Container, SlyTqdm
import src.globals as g
import pandas as pd
import numpy as np
import open3d as o3d
from supervisely.geometry.cuboid_3d import Cuboid3d
from supervisely import (
    PointcloudFigure,
    PointcloudDataset,
    PointcloudEpisodeDataset,
    PointcloudEpisodeAnnotation,
    PointcloudAnnotation,
)

lines = None
cols = [
    "id",
    "object id",
    "link",
    "labeler",
    "class",
    "geometry",
    "volume",
    "points inside",
    "size x",
    "size y",
    "size z",
    "position x",
    "position y",
    "position z",
    "rotation dx",
    "rotation dy",
    "rotation dz",
]
cols = list(map(str.upper, cols))

progress = SlyTqdm()
progress.hide()
table = Table(fixed_cols=1, width="100%")
START_LOCK_MESSAGE = "Please wait..."

card = Card(
    "4️⃣ Labels (Figures)",
    collapsable=True,
    content=Container([progress, table], gap=0),
    lock_message=START_LOCK_MESSAGE,
)
card.lock()


def build_table(round_floats=4):
    global lines, table, cols, progress
    if lines is None:
        lines = []
    table.loading = True
    progress.show()

    with progress(message="Calculating labels stats...", total=g.project_fs.total_items) as pbar:
        ds_infos = g.api.dataset.get_list(g.project_id)
        for ds in g.project_fs.datasets:
            ds_id = None
            for ds_info in ds_infos:
                if ds_info.name == ds.name:
                    ds_id = ds_info.id

            for item_name in ds:
                item_info = ds.get_pointcloud_info(item_name)
                paths = ds.get_item_paths(item_name)
                ptc_path = paths.pointcloud_path
                if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                    ds: PointcloudDataset
                    ann: PointcloudAnnotation = ds.get_ann(item_name, g.project_meta)
                    figs = ann.figures
                    labeling_url = sly.pointcloud.get_labeling_tool_url(ds_id, item_info.id)
                    labeling_tool_link = sly.pointcloud.get_labeling_tool_link(
                        labeling_url, item_name
                    )
                elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                    ds: PointcloudEpisodeDataset
                    ann: PointcloudEpisodeAnnotation = ds.get_ann(g.project_meta)
                    frame_idx = ds.get_frame_idx(item_name)
                    figs = ann.get_figures_on_frame(frame_idx)

                    labeling_url = sly.pointcloud_episodes.get_labeling_tool_url(
                        ds_id, item_info.id
                    )
                    labeling_tool_link = sly.pointcloud_episodes.get_labeling_tool_link(
                        labeling_url, item_name
                    )
                pcd = o3d.io.read_point_cloud(ptc_path)
                pcd_np = np.asarray(pcd.points)

                for fig in figs:
                    fig: PointcloudFigure
                    if not isinstance(fig.geometry, Cuboid3d):
                        continue
                    size = fig.geometry.dimensions
                    pos = fig.geometry.position
                    rot = fig.geometry.rotation
                    volume = size.x * size.y * size.z

                    points_inside = pcd_np[
                        (pcd_np[:, 0] >= pos.x - size.x * 0.5)
                        & (pcd_np[:, 0] <= pos.x + size.x * 0.5)
                        & (pcd_np[:, 1] >= pos.y - size.y * 0.5)
                        & (pcd_np[:, 1] <= pos.y + size.y * 0.5)
                        & (pcd_np[:, 2] >= pos.z - size.z * 0.5)
                        & (pcd_np[:, 2] <= pos.z + size.z * 0.5)
                    ]
                    lines.append(
                        [
                            g.project_fs.key_id_map.get_figure_id(fig.key()),
                            g.project_fs.key_id_map.get_object_id(fig.parent_object.key()),
                            labeling_tool_link,
                            fig.labeler_login,
                            fig.parent_object.obj_class.name,
                            fig.geometry.geometry_name(),
                            round(volume, round_floats),
                            len(points_inside),
                            round(size.x, round_floats),
                            round(size.y, round_floats),
                            round(size.z, round_floats),
                            round(pos.x, round_floats),
                            round(pos.y, round_floats),
                            round(pos.z, round_floats),
                            round(rot.x, round_floats),
                            round(rot.y, round_floats),
                            round(rot.z, round_floats),
                        ]
                    )
                pbar.update()
    df = pd.DataFrame(lines, columns=cols)
    table.read_pandas(df)
    table.loading = False
    progress.hide()
