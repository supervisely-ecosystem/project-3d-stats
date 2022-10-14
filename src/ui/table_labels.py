import supervisely as sly
from supervisely.app.widgets import Card, Table
import src.globals as g
import pandas as pd
import numpy as np
import open3d as o3d
from supervisely.video_annotation.key_id_map import KeyIdMap
from supervisely.geometry.cuboid_3d import Cuboid3d

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

table = Table(fixed_cols=1, width="100%")
START_LOCK_MESSAGE = "Please wait..."

card = Card(
    "4️⃣ Labels (Figures)",
    collapsable=True,
    content=table,
    lock_message=START_LOCK_MESSAGE,
)
card.lock()


def build_table(progress, round_floats=4):
    global lines, table, cols
    if lines is None:
        lines = []
    table.loading = True

    with progress(message=f"Calculating labels stats...", total=g.project_fs.total_items) as pbar:
        for ds in g.project_fs.datasets:
            ds_id = g.project_fs.key_id_map.get_video_id(ds.key())

            if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                ptc_infos = g.api.pointcloud.get_list(ds_id)
            elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                ptc_infos = g.api.pointcloud_episode.get_list(ds_id)
                ann_path = ds.get_ann_path()
                ann_json = sly.json.load_json_file(ann_path)
                ann = sly.PointcloudEpisodeAnnotation.from_json(
                    ann_json, g.project_meta, g.project_fs.key_id_map
                )
                frame_ptc_map_path = ds.get_frame_pointcloud_map_path()
                frame_ptc_map = sly.json.load_json_file(frame_ptc_map_path)
                ptc_frame_map = {v: k for k, v in frame_ptc_map.items()}

            for item in ptc_infos:

                if g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                    paths = ds.get_item_paths(item.name)
                    ptc_path = paths.pointcloud_path
                    ann_path = paths.ann_path
                    ann_json = sly.json.load_json_file(ann_path)
                    ann = sly.PointcloudAnnotation.from_json(
                        ann_json, g.project_meta, g.project_fs.key_id_map
                    )
                    figs = ann.figures
                    labeling_url = sly.pointcloud.get_labeling_tool_url(ds_id, item.id)
                    labeling_tool_link = sly.pointcloud.get_labeling_tool_link(
                        labeling_url, item.name
                    )

                elif g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                    paths = ds.get_item_paths(item.name)
                    ptc_path = paths.pointcloud_path
                    current_frame = ann.frames.get(int(ptc_frame_map[item.name]))
                    figs = current_frame.figures
                    labeling_url = sly.pointcloud_episodes.get_labeling_tool_url(ds_id, item.id)
                    labeling_tool_link = sly.pointcloud_episodes.get_labeling_tool_link(
                        labeling_url, item.name
                    )
                pcd = o3d.io.read_point_cloud(ptc_path)
                pcd_np = np.asarray(pcd.points)

                for fig in figs:
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
