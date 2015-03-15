from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from sqlalchemy import Column, types

import transaction

from ... import model

from .base import ModelTest


class TestImagesModel(ModelTest):

    @classmethod
    def _setup_once_schema(cls):
        class Book(model.Base, model.ImageMixin):
            __tablename__ = 'test_books'
            __table_args__ = {'mysql_engine': 'InnoDB'}
            id = Column(types.Integer, primary_key=True)
            data = Column(types.String(255))

        cls.Book = Book
        engine = model.Base.metadata.bind
        cls.Book.__table__.create(bind=engine)
        cls.Book.ImageAssociation.__table__.create(bind=engine)

    def _setup_each_data(self):
        book_a = self.Book()
        model.Session.add(book_a)
        for ii in range(3):
            book_a.image_metas.append(
                model.ImageMeta(name='imtest%d' % ii,
                                original_ext='jpg'))
        self.im = book_a.image_metas[0]

        book_b = self.Book()
        model.Session.add(book_b)
        model.Session.flush()
        self.book_a_id = book_a.id
        self.book_b_id = book_b.id

    def _teardown_each(self):
        self._clear_classes(self.Book,
                            self.Book.ImageAssociation,
                            model.ImageMeta)

    def test_append(self):
        with transaction.manager:
            book = self.Book.get(self.book_a_id)
            book.image_metas.append(
                model.ImageMeta(name='imtest3', original_ext='jpg'))

        book2 = self.Book.get(self.book_a_id)
        self.assertEqual([im.name for im in book2.image_metas],
                         ['imtest0', 'imtest1', 'imtest2', 'imtest3'])
