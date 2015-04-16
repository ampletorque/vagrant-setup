from unittest import TestCase
from sqlalchemy import create_engine

import transaction

from ... import model


class ModelTest(TestCase):
    """
    Parent class for model tests. The goal of providing this is for the model
    test to be able to create and destroy fixtures without impacting any state
    outside of the test class.
    """
    @classmethod
    def save_model_state(cls):
        cls.orig_engine = model.Base.metadata.bind

    @classmethod
    def restore_model_state(cls):
        model.Base.metadata.bind = cls.orig_engine
        model.Session.remove()

    @classmethod
    def setUpClass(cls):
        cls.save_model_state()

        engine = create_engine('sqlite:///')
        model.Session.remove()
        model.init_model(engine)

        model.Base.metadata.create_all()

        cls._setup_once_schema()
        cls._setup_once_data()
        transaction.commit()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_once()
        cls.restore_model_state()

    def setUp(self):
        self._setup_each_schema()
        self._setup_each_data()
        transaction.commit()

    def tearDown(self):
        self._teardown_each()
        transaction.commit()

    @classmethod
    def _setup_once_schema(self):
        """
        Override to setup schema that will be used for the duration of the
        class.
        """

    @classmethod
    def _setup_once_data(self):
        """
        Override to setup data that will be used for the duration of the class.
        """

    @classmethod
    def _teardown_once(self):
        """
        Override to teardown anything setup for this class.
        """

    def _setup_each_schema(self):
        """
        Override to setup schema that will be used for each method.
        """

    def _setup_each_data(self):
        """
        Override to setup data that will be used for each method.
        """

    def _teardown_each(self):
        """
        Override to teardown anything used for each method.
        """

    def _clear_classes(self, *classes):
        for cls in classes:
            for obj in model.Session.query(cls):
                model.Session.delete(obj)

    def assertJoined(self, q, cls):
        joined_classes = set(to_mapper.class_ for from_mapper, to_mapper, along
                             in q._joinpath.keys())
        self.assertIn(cls, joined_classes)
