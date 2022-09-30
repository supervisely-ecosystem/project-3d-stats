import os
import supervisely as sly

api = sly.Api()

project_id = int(os.environ["context.projectId"])
project_info = api.project.get_info_by_id(project_id)
meta_json = api.project.get_meta(project_id)
project_meta = sly.ProjectMeta.from_json(meta_json)
