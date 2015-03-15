from . import model


def get_project(project_id):
    return model.Project.get(project_id)
