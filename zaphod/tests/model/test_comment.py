from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, types

from ... import model

from .base import ModelTest


class TestComment(ModelTest):

    @classmethod
    def _setup_once_schema(cls):
        class Movie(model.Base, model.CommentMixin):
            __tablename__ = 'test_movies'
            __table_args__ = {'mysql_engine': 'InnoDB'}
            id = Column(types.Integer, primary_key=True)
            data = Column(types.String(255))

        cls.Movie = Movie
        engine = model.Base.metadata.bind
        cls.Movie.__table__.create(bind=engine)
        cls.Movie.Comment.__table__.create(bind=engine)

    @classmethod
    def _setup_once_data(cls):
        user = model.User(name='Test User', email='test@example.com')
        model.Session.add(user)

        movie_a = cls.Movie()
        model.Session.add(movie_a)
        movie_a.add_comment(user, 'A test comment.')

        model.Session.flush()

        cls.user_id = user.id
        cls.movie_id = movie_a.id

    def test_comments(self):
        movie = self.Movie.get(self.movie_id)
        self.assertEqual(len(movie.comments), 1)
        self.assertEqual(movie.comments[0].created_by.id, self.user_id)
        self.assertEqual(movie.comments[0].body, 'A test comment.')

    def test_new_comment(self):
        movie = self.Movie()
        self.assertIsNone(movie.new_comment)
        user = model.User.get(self.user_id)

        movie.new_comment = (user, 'Hello, world.')
        self.assertEqual(len(movie.comments), 1)
        self.assertEqual(movie.comments[0].created_by, user)
        self.assertEqual(movie.comments[0].body, 'Hello, world.')
