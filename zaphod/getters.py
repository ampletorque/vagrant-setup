from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from . import model


def get_project(project_id):
    return model.Project.get(project_id)
