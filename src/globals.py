import os
import sys
from typing import Union
from pathlib import Path
import supervisely as sly

api = sly.Api()

project_id = int(os.environ["context.projectId"])
project_info: sly.ProjectInfo = api.project.get_info_by_id(project_id)
project_type: str = project_info.type
project_meta: sly.ProjectMeta = None

# TODO: change path
app_root_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {app_root_dir}")

# TODO: check where is data_dir
project_dir = os.path.join(app_root_dir, "sly_project")
project_fs: Union[sly.PointcloudEpisodeProject, sly.PointcloudProject] = None
