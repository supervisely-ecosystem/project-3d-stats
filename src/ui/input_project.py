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
import src.ui.table_classes as classes
import src.ui.table_labels as labels
import src.ui.table_datasets as datasets
import src.main as main

select_project = SelectProject(g.project_id)
project_thumbnail = ProjectThumbnail(g.project_info)
project_thumbnail.hide()
download_btn = Button("DOWNLOAD PROJECT AND CALCULATE STATS", icon="zmdi zmdi-download")
progress = SlyTqdm()
progress.hide()

finish_msg = sly.app.widgets.Text("Stats have been calculated successfully.", status="success")
finish_msg.hide()

card = Card(
    "1️⃣ Input Project",
    "Select project to show stats",
    collapsable=True,
    content=Container(
        [
            select_project,
            project_thumbnail,
            progress,
            download_btn,
            finish_msg,
        ],
        gap=5,
    ),
)


@download_btn.click
def download():
    progress.show()
    if not sly.fs.dir_exists(g.project_dir):
        sly.fs.mkdir(g.project_dir)
        if g.project_type == str(sly.ProjectType.POINT_CLOUD_EPISODES):
            with progress(
                message="Downloading pointcloud episodes project...",
                total=g.project_info.items_count,
            ) as pbar:
                sly.PointcloudEpisodeProject.download(
                    g.api,
                    g.project_id,
                    g.project_dir,
                    dataset_ids=None,
                    download_pointclouds=True,
                    download_related_images=True,
                    download_pointclouds_info=True,
                    log_progress=True,
                    progress_cb=pbar.update,
                )
        elif g.project_type == str(sly.ProjectType.POINT_CLOUDS):
            with progress(
                message="Downloading pointcloud project...",
                total=g.project_info.items_count,
            ) as pbar:
                sly.PointcloudProject.download(
                    g.api,
                    g.project_id,
                    g.project_dir,
                    dataset_ids=None,
                    log_progress=True,
                    download_pointclouds=True,
                    download_related_images=True,
                    download_pointclouds_info=True,
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
    progress.hide()
    project_thumbnail.show()
    pointclouds.card.uncollapse()
    pointclouds.card.unlock()
    pointclouds.build_table()
    classes.card.uncollapse()
    classes.card.unlock()
    classes.build_table()
    labels.card.uncollapse()
    labels.card.unlock()
    labels.build_table()
    datasets.card.uncollapse()
    datasets.card.unlock()
    datasets.build_table()
    finish_msg.show()
    main.app.shutdown()
