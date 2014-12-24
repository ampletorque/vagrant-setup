from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os.path
import sys

import transaction

from sqlalchemy import create_engine, engine_from_config
from pyramid.paster import get_appsettings, setup_logging

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from .. import model


old_url = 'mysql+pymysql://crowdsupply:quux@localhost/crowdsupply?charset=utf8'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def migrate_aliases(old_node, new_node):
    canonical_path = None
    for alias in old_node.aliases:
        print("  path: %s" % alias.path)
        if alias.canonical:
            canonical_path = alias.path
        new_node.update_path(alias.path)
    if canonical_path:
        new_node.update_path(canonical_path)


def migrate_tags(user_map):
    tag_map = {}
    for old_tag in scrappy_meta.Session.query(cs_model.Tag):
        print("tag %s" % old_tag.name)
        tag = model.Tag(
            name=old_tag.name,
            teaser=old_tag.name,
            body=old_tag.body.text,
            published=old_tag.published,
            listed=old_tag.listed,
        )
        model.Session.add(tag)
        migrate_aliases(old_tag, tag)
        tag_map[old_tag] = tag
    return tag_map


def migrate_creators(user_map):
    creator_map = {}
    for old_creator in scrappy_meta.Session.query(cs_model.Creator):
        print("creator %s" % old_creator.name)
        creator = model.Creator(
            name=old_creator.name,
            teaser=old_creator.teaser,
            body=old_creator.body.text,
            published=old_creator.published,
            listed=old_creator.listed,
        )
        model.Session.add(creator)
        migrate_aliases(old_creator, creator)
        creator_map[old_creator] = creator
    return creator_map


def migrate_projects(user_map, creator_map, tag_map):
    project_map = {}
    for old_project in scrappy_meta.Session.query(cs_model.Project):
        print("  project %s" % old_project.name)
        project = model.Project(
            creator=creator_map[old_project.creator],
            name=old_project.name,
            teaser=old_project.teaser,
            body=old_project.body.text,
            published=old_project.published,
            listed=old_project.listed,
        )
        model.Session.add(project)
        migrate_aliases(old_project, project)
        project_map[old_project] = project
        for old_tag in old_project.tags:
            print("    assoc tag %s" % old_tag.name)
            project.tags.add(tag_map[old_tag])


def migrate_users():
    user_map = {}
    return user_map


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = engine_from_config(settings, 'sqlalchemy.')
    model.Session.configure(bind=engine)
    model.Base.metadata.drop_all(engine)
    model.Base.metadata.create_all(engine)

    old_engine = create_engine(old_url)
    scrappy_model.init_model(old_engine, site_map={})

    with transaction.manager:
        user_map = migrate_users()
        tag_map = migrate_tags(user_map)
        creator_map = migrate_creators(user_map)
        project_map = migrate_projects(user_map, creator_map, tag_map)
        print(project_map)
