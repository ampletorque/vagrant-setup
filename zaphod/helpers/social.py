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


def gplus_share_url(url):
    return 'https://plus.google.com/share?%s' % (
        urlencode(dict(url=url)))
