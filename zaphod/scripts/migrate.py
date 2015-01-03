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


def migrate_aliases(settings, old_node, new_node):
    canonical_path = None
    for alias in old_node.aliases:
        print("  path: %r" % alias.path)
        if alias.canonical:
            canonical_path = alias.path
        new_node.update_path(alias.path)
    if canonical_path:
        new_node.update_path(canonical_path)


def migrate_images(settings):
    image_map = {}
    for old_im in scrappy_meta.Session.query(scrappy_model.ImageMeta):
        print("image %s" % old_im.name)
        new_im = model.ImageMeta(
            name=old_im.name,
            alt=old_im.alt,
            title=old_im.title,
            original_ext=old_im.original_ext,
            width=old_im.width,
            height=old_im.height,
            created_time=old_im.created_time,
            updated_time=old_im.updated_time,
        )
        model.Session.add(new_im)
        # XXX Copy the actual image path!
        # XXX Copy image type?
        image_map[old_im] = new_im
    return image_map


def migrate_image_associations(settings, image_map, old_obj, new_obj):
    for old_im in old_obj.image_metas:
        print("  image assoc %s" % old_im.name)
        new_obj.image_metas.append(image_map[old_im])


def migrate_articles(settings, user_map, image_map):
    for old_article in scrappy_meta.Session.query(scrappy_model.Article):
        print("article %s" % old_article.name)
        article = model.Article(
            name=old_article.name,
            teaser=old_article.teaser,
            body=old_article.body.text,
            published=old_article.published,
            listed=old_article.listed,
            show_heading=old_article.show_heading,
            show_article_list=old_article.show_article_list,
            category=old_article.category,
            created_by=user_map[old_article.created_by],
            created_time=old_article.created_time,
            updated_by=user_map[old_article.updated_by],
            updated_time=old_article.updated_time,
        )
        model.Session.add(article)
        migrate_aliases(settings, old_article, article)
        migrate_image_associations(settings, image_map, old_article, article)
        model.Session.flush()


def migrate_tags(settings, user_map):
    tag_map = {}
    for old_tag in scrappy_meta.Session.query(cs_model.Tag):
        print("tag %s" % old_tag.name)
        tag = model.Tag(
            name=old_tag.name,
            teaser=old_tag.name,
            body=old_tag.body.text,
            published=old_tag.published,
            listed=old_tag.listed,
            created_by=user_map[old_tag.created_by],
            created_time=old_tag.created_time,
            updated_by=user_map[old_tag.updated_by],
            updated_time=old_tag.updated_time,
        )
        model.Session.add(tag)
        migrate_aliases(settings, old_tag, tag)
        tag_map[old_tag] = tag
        model.Session.flush()
    return tag_map


def migrate_creators(settings, user_map, image_map):
    creator_map = {}
    for old_creator in scrappy_meta.Session.query(cs_model.Creator):
        print("creator %s" % old_creator.name)
        creator = model.Creator(
            name=old_creator.name,
            teaser=old_creator.teaser,
            body=old_creator.body.text,
            published=old_creator.published,
            listed=old_creator.listed,
            created_by=user_map[old_creator.created_by],
            created_time=old_creator.created_time,
            updated_by=user_map[old_creator.updated_by],
            updated_time=old_creator.updated_time,
        )
        model.Session.add(creator)
        migrate_aliases(settings, old_creator, creator)
        migrate_image_associations(settings, image_map, old_creator, creator)
        creator_map[old_creator] = creator
        model.Session.flush()
    return creator_map


def migrate_projects(settings, user_map, creator_map, tag_map, image_map):
    project_map = {}
    pledge_level_map = {}
    for old_project in scrappy_meta.Session.query(cs_model.Project):
        print("  project %s" % old_project.name)
        project = model.Project(
            creator=creator_map[old_project.creator],
            name=old_project.name,

            prelaunch_vimeo_id=None,
            prelaunch_teaser=old_project.teaser,
            prelaunch_body=u'',

            crowdfunding_vimeo_id=old_project.vimeo_id,
            crowdfunding_teaser=old_project.teaser,
            crowdfunding_body=old_project.body.text,

            available_vimeo_id=old_project.vimeo_id,
            available_teaser=old_project.teaser,
            available_body=old_project.body.text,

            published=old_project.published,
            listed=old_project.listed,
            gravity=old_project.gravity,
            target=old_project.target,
            start_time=old_project.start_time,
            end_time=old_project.end_time,
            suspended_time=old_project.suspended_time,
            created_by=user_map[old_project.created_by],
            created_time=old_project.created_time,
            updated_by=user_map[old_project.updated_by],
            updated_time=old_project.updated_time,
        )
        model.Session.add(project)
        migrate_aliases(settings, old_project, project)
        migrate_image_associations(settings, image_map, old_project, project)
        project_map[old_project] = project
        for old_tag in old_project.tags:
            print("    assoc tag %s" % old_tag.name)
            project.tags.add(tag_map[old_tag])
        for old_update in old_project.updates:
            print("    update %s" % old_update.name)
            update = model.ProjectUpdate(
                project=project,
                name=old_update.name,
                teaser=old_update.teaser,
                body=old_update.body.text,
                published=old_update.published,
                listed=old_update.listed,
                created_by=user_map[old_update.created_by],
                created_time=old_update.created_time,
                updated_by=user_map[old_update.updated_by],
                updated_time=old_update.updated_time,
            )
            model.Session.add(update)
            migrate_aliases(settings, old_update, update)
            migrate_image_associations(settings, image_map, old_update, update)
        for old_pledge_level in old_project.levels:
            print("    pledge level %s" % old_pledge_level.name)
            pledge_level = model.PledgeLevel(
                project=project,
                name=old_pledge_level.name,
                non_physical=old_pledge_level.non_physical,
                gravity=old_pledge_level.gravity,
                published=old_pledge_level.published,
                price=old_pledge_level.price,
            )
            model.Session.add(pledge_level)
            migrate_image_associations(settings, image_map,
                                       old_pledge_level, pledge_level)
            pledge_level_map[old_pledge_level] = pledge_level
        model.Session.flush()
    return project_map, pledge_level_map


def migrate_users(settings, image_map):
    user_map = {}
    user_emails = set()
    for old_user in scrappy_meta.Session.query(scrappy_model.Account).\
            order_by(scrappy_model.Account.id.desc()):
        print("  user %s" % old_user.email)

        if old_user.id == 1:
            user_map[old_user] = model.User.get(1)
            continue

        if old_user.email in user_emails:
            email = old_user.email + '.' + str(old_user.id)
        else:
            email = old_user.email

        user_emails.add(old_user.email)

        user = model.User(
            id=old_user.id,
            name=old_user.name,
            email=email,
            hashed_password=old_user.hashed_password,
            enabled=old_user.enabled,
            created_time=old_user.created_time,
            updated_time=old_user.updated_time,
        )
        model.Session.add(user)
        migrate_image_associations(settings, image_map, old_user, user)
        user_map[old_user] = user
        model.Session.flush()

    # Take a second pass through to set the updated by / created by.
    for old_user in scrappy_meta.Session.query(scrappy_model.Account).\
            order_by(scrappy_model.Account.id.desc()):
        new_user = user_map[old_user]
        new_user.updated_by = user_map[old_user.updated_by]
        new_user.created_by = user_map[old_user.created_by]

    # Set image updated by / created by.
    for old_image, new_image in image_map.items():
        new_image.updated_by = user_map[old_image.updated_by]
        new_image.created_by = user_map[old_image.created_by]

    return user_map


def migrate_provider_types(settings, user_map, image_map):
    provider_type_map = {}
    for old_provider_type in \
            scrappy_meta.Session.query(cs_model.ProviderType):
        print("  provider type %s" % old_provider_type.name)
        provider_type = model.ProviderType(
            name=old_provider_type.name,
            teaser=old_provider_type.teaser,
            body=old_provider_type.body.text,
            published=old_provider_type.published,
            listed=old_provider_type.listed,
            created_by=user_map[old_provider_type.created_by],
            created_time=old_provider_type.created_time,
            updated_by=user_map[old_provider_type.updated_by],
            updated_time=old_provider_type.updated_time,
        )
        model.Session.add(provider_type)
        migrate_aliases(settings, old_provider_type, provider_type)
        migrate_image_associations(settings, image_map,
                                   old_provider_type, provider_type)
        provider_type_map[old_provider_type] = provider_type
        model.Session.flush()
    return provider_type_map


def migrate_providers(settings, user_map, image_map, provider_type_map):
    for old_provider in scrappy_meta.Session.query(cs_model.Provider):
        print("  provider %s" % old_provider.name)
        provider = model.Provider(
            name=old_provider.name,
            teaser=old_provider.teaser,
            body=old_provider.body.text,
            published=old_provider.published,
            listed=old_provider.listed,
            created_by=user_map[old_provider.created_by],
            created_time=old_provider.created_time,
            updated_by=user_map[old_provider.updated_by],
            updated_time=old_provider.updated_time,
        )
        model.Session.add(provider)
        for old_type in old_provider.types:
            provider.types.add(provider_type_map[old_type])
        migrate_aliases(settings, old_provider, provider)
        migrate_image_associations(settings, image_map, old_provider, provider)
        model.Session.flush()


def migrate_orders(settings, user_map, pledge_level_map):
    for old_order in scrappy_meta.Session.query(scrappy_model.Order):
        print("  order %s" % old_order.id)
        if old_order.account:
            user = user_map[old_order.account]
        else:
            user = None
        order = model.Order(
            id=old_order.id,
            user=user,
            created_by=user_map[old_order.created_by],
            created_time=old_order.created_time,
            updated_by=user_map[old_order.updated_by],
            updated_time=old_order.updated_time,
        )
        model.Session.add(order)
        cart = model.Cart(order=order)
        model.Session.add(cart)
        for old_ci in old_order.cart.items:
            ci = model.CartItem(
                pledge_level=pledge_level_map[old_ci.product],
                price_each=old_ci.price_each,
                qty_desired=old_ci.qty_desired,
            )
            order.cart.items.append(ci)
        model.Session.flush()


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
    scrappy_model.init_model(old_engine, site_map={}, default_site_id=701)

    with transaction.manager:
        root_user = model.User(
            name=u'Root User',
            email='root@crowdsupply.com',
        )
        root_user.update_password('root')
        model.Session.add(root_user)
        model.Session.flush()

        image_map = migrate_images(settings)
        user_map = migrate_users(settings, image_map)

        provider_type_map = migrate_provider_types(settings, user_map,
                                                   image_map)
        migrate_providers(settings, user_map, image_map, provider_type_map)

        migrate_articles(settings, user_map, image_map)
        tag_map = migrate_tags(settings, user_map)
        creator_map = migrate_creators(settings, user_map, image_map)
        project_map, pledge_level_map = \
            migrate_projects(settings, user_map, creator_map,
                             tag_map, image_map)
        migrate_orders(settings, user_map, pledge_level_map)
