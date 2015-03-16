from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

from .. import model


def populate_content():
    creator1 = model.Creator(
        name='Widgets International',
        published=True,
        listed=True,
    )
    creator1.update_path(creator1.generate_path())
    model.Session.add(creator1)

    creator2 = model.Creator(
        name='Carrot Labs',
        published=True,
        listed=True,
    )
    creator2.update_path(creator2.generate_path())
    model.Session.add(creator2)

    model.Session.flush()

    project1 = model.Project(
        name='Premium Widget',
        teaser='The best widget in the west!',
        creator=creator1,
        start_time=datetime(2015, 4, 1),
        end_time=datetime(2015, 5, 1),
        target=5000,
        published=True,
        listed=True,
    )
    project1.update_path(project1.generate_path())
    model.Session.add(project1)

    project2 = model.Project(
        name='iPadded Tablet Sleeve',
        teaser='We forgot to make the first one padded.',
        creator=creator2,
        start_time=datetime(2014, 9, 12),
        end_time=datetime(2014, 11, 5),
        target=50000,
        published=True,
        listed=True,
    )
    project2.update_path(project2.generate_path())
    model.Session.add(project2)

    project3 = model.Project(
        name='Laptop Case',
        teaser='This campaign will succeed, surely.',
        creator=creator2,
        start_time=datetime(2015, 1, 2),
        end_time=datetime(2015, 2, 28),
        target=500,
        published=True,
        listed=True,
    )
    project3.update_path(project3.generate_path())
    model.Session.add(project3)

    article = model.Article(
        name='Infrequently Asked Questions',
        body='## Questions\n\nNot to be asked *often*.',
        published=True,
        listed=True,
    )
    article.update_path(article.generate_path())
    model.Session.add(article)

    tags = {}
    for name in ('Lifestyle', 'Technology', 'Accessories'):
        tag = model.Tag(
            name=name,
            published=True,
            listed=True,
        )
        tag.update_path(tag.generate_path())
        model.Session.add(tag)
        tags[name] = tag

    tag = model.Tag(
        name='Unlisted Tag',
        published=True,
        listed=False,
    )
    tag.update_path(tag.generate_path())
    model.Session.add(tag)
    tags[tag.name] = tag
