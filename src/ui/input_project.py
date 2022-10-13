import supervisely as sly
from supervisely.app.widgets import (
    Card,
    ProjectThumbnail,
    Button,
    SlyTqdm,
    Container,
    SelectProject,
)
import src.globals as g
import src.ui.table_pointclouds as pointclouds

select_project = SelectProject(g.project_id)
project_thumbnail = ProjectThumbnail(g.project_info)
project_thumbnail.hide()
download_btn = Button("DOWNLOAD PROJECT AND CALCULATE STATS", icon="zmdi zmdi-download")
download_progress = SlyTqdm()
finish_msg = sly.app.widgets.Text("Stats have been calculated successfully.", status="success")
finish_msg.hide()

card = Card(
    "1️⃣ Input Project",
    "Select project to show stats",
    collapsable=True,
    content=Container(
        [select_project, project_thumbnail, download_progress, download_btn, finish_msg]
    ),
)


@download_btn.click
def download():
    if not sly.fs.dir_exists(g.project_dir):
        sly.fs.mkdir(g.project_dir)
        with download_progress(
            message=f"Downloading project...", total=g.project_info.items_count
        ) as pbar:
            if g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
                sly.download_pointcloud_episode_project(
                    g.api,
                    g.project_id,
                    g.project_dir,
                    dataset_ids=None,
                    download_related_images=False,
                    log_progress=False,
                    progress_cb=pbar.update,
                )
            elif g.project_type == str(sly.ProjectType.POINT_CLOUDS):
                sly.download_pointcloud_project(
                    g.api,
                    g.project_id,
                    g.project_dir,
                    dataset_ids=None,
                    log_progress=False,
                    progress_cb=pbar.update,
                )
    if g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
        g.project_fs = sly.PointcloudEpisodeProject(g.project_dir, sly.OpenMode.READ)
    elif g.project_type == str(sly.ProjectType.POINT_CLOUDS):
        g.project_fs = sly.PointcloudProject(g.project_dir, sly.OpenMode.READ)

    g.project_meta = g.project_fs.meta
    sly.logger.info(f"Project data: {g.project_fs.total_items} point clouds")
    select_project.hide()
    download_btn.hide()
    project_thumbnail.show()
    finish_msg.show()
    pointclouds.card.uncollapse()
    pointclouds.card.unlock()
    pointclouds.build_table(download_progress)
