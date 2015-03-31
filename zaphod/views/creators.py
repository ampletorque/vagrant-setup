from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.sql import and_
from pyramid.view import view_config

from .. import model


@view_config(route_name='creators', renderer='creators.html')
def creators_view(request):
    q = model.Session.query(model.Creator).\
        join(model.Creator.aliases).\
        filter(model.Creator.published == True).\
        filter(model.Creator.projects.any(
            and_(model.Project.published == True,
                 model.Project.start_time < model.utcnow()),
        )).\
        order_by(model.Creator.name)
    return dict(creators=q.all())
