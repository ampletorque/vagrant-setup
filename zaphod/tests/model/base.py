from unittest import TestCase
from sqlalchemy import create_engine

from ... import model


class ModelTest(TestCase):
    """
    Parent class for model tests. The goal of providing this is for the model
    test to be able to create and destroy fixtures without impacting any state
    outside of the test class.
    """
    @classmethod
    def save_model_state(cls):
        cls.orig_engine = model.Base.metadata.engine
        cls.orig_session = model.Session

    @classmethod
    def restore_model_state(cls):
        model.Base.metadata.bind = cls.orig_engine
        model.Session = cls.orig_session

    @classmethod
    def setUpClass(cls):
        cls.save_model_state()

        engine = create_engine('sqlite:///')
        model.Session.configure(bind=engine)
        model.Base.metadata.create_all()

        cls._setup_once_schema()
        cls._setup_once_data()
        model.Session.commit()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_once()
        cls.restore_model_state()

    def setUp(self):
        super(ModelTest, self).setUp()
        self._setup_each_schema()
        self._setup_each_data()
        model.Session.commit()

    def tearDown(self):
        if model.Session and not model.Session.is_active:
            model.Session.rollback()
        self._teardown_each()
        model.Session.commit()

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
        model.Session.commit()

    def assertJoined(self, q, cls):
        joined_classes = set(to_mapper.class_ for from_mapper, to_mapper, along
                             in q._joinpath.keys())
        self.assertIn(cls, joined_classes)
