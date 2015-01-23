from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from six.moves.urllib.parse import urlencode


def twitter_tweet_url(text, url, via):
    text = text.encode('ascii', 'ignore')
    return 'https://twitter.com/intent/tweet?%s' % (
        urlencode(dict(text=text, via=via, url=url)))


def facebook_share_url(text, url, name, caption, image_url, app_id,
                       redirect_uri):
    text = text.encode('ascii', 'ignore')
    name = name.encode('ascii', 'ignore')
    caption = caption.encode('ascii', 'ignore')
    return 'https://www.facebook.com/dialog/feed?%s' % (
        urlencode(dict(app_id=app_id,
                       link=url,
                       picture=image_url,
                       name=name,
                       caption=caption,
                       description=text,
                       redirect_uri=redirect_uri)))


def pin_it_url(dst_url, media, description):
    # XXX Pinterest doesn't seem to want to use https for this right now, but
    # check back later.
    return "http://pinterest.com/pin/create/button/?%s" % (
        urlencode(dict(url=dst_url, media=media, description=description)))


def gplus_share_url(url):
    return 'https://plus.google.com/share?%s' % (
        urlencode(dict(url=url)))


def project_facebook_url(request, project):
    return facebook_share_url(
        text=project.teaser,
        url=request.node_url(project),
        name=project.name,
        caption='Funding on Crowd Supply',
        image_url=project.img_url(request, 'project-main'),
        app_id=request.registry.settings['facebook.app_id'],
        redirect_uri=request.url)


def project_twitter_url(request, project):
    return twitter_tweet_url(
        text='Check out this crowdfunding project!',
        via='crowd_supply',
        url=request.node_url(project))


def project_pin_it_url(request, project):
    # XXX Consider adding 'pinset' support to this.
    return pin_it_url(
        dst_url=request.node_url(project),
        media=project.img_url(request, 'project-main'),
        # media=request.route_url('pinset', id=project.id),
        description='Funding on Crowd Supply',
    )
