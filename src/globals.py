import os
from typing import Union
import supervisely as sly

api = sly.Api()

project_id = int(os.environ["context.projectId"])
project_info: sly.ProjectInfo = api.project.get_info_by_id(project_id)
project_type: str = project_info.type
project_meta: sly.ProjectMeta = None

data_dir = sly.app.get_data_dir()
sly.logger.info(f"Data directory: {data_dir}")

# sly.fs.clean_dir(data_dir)

project_dir = os.path.join(data_dir, "sly_project")
project_fs: Union[sly.PointcloudEpisodeProject, sly.PointcloudProject] = None
