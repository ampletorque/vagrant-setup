from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

import transaction

from ... import model

from .base import ModelTest


class TestProject(ModelTest):
    @classmethod
    def _setup_once_data(cls):
        creator = model.Creator(
            name=u'Amateur Cryogenics',
        )
        creator.update_path(creator.generate_path())
        model.Session.add(creator)
        model.Session.flush()

        project = model.Project(
            creator=creator,
            name=u'Freeze-a-Friend 3000',
            target=10000,
            start_time=datetime(2015, 1, 1),
            end_time=datetime(2015, 3, 1),
        )
        project.update_path(project.generate_path())
        model.Session.add(project)

        product = model.Product(
            project=project,
            price=20,
        )
        model.Session.add(product)
        model.Session.flush()

        cls.creator_id = creator.id
        cls.project_id = project.id
        cls.product_id = product.id

    def test_generate_path(self):
        project = model.Project.get(self.project_id)
        self.assertEqual(project.generate_path(),
                         'amateur-cryogenics/freeze-a-friend-3000')

    def test_is_live(self):
        pass

    def test_status(self):
        pass

    def test_progress_percent(self):
        pass

    def test_pledged_amount(self):
        pass

    def test_num_backers(self):
        pass

    def test_num_pledges(self):
        pass

    def test_final_day(self):
        pass

    def test_remaining(self):
        pass

    def test_elastic_mapping(self):
        pass
