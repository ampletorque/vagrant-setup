from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from urllib import urlencode

from webhelpers2.html import HTML, tags


def twitter_follow_button(name, show_follower_count=True):
    twitter_url = "http://twitter.com/%s" % name
    link_text = "Follow @%s" % name
    show_count = str(bool(show_follower_count)).lower()

    return HTML.a(link_text, href=twitter_url,
                  class_="twitter-follow-button",
                  **{"data-show-count": show_count})


def pin_it_url(dst_url, media, description):
    return "http://pinterest.com/pin/create/button/?%s" % (
        urlencode(dict(url=dst_url, media=media, description=description)))


def pinterest_follow_url(username):
    return "http://pinterest.com/%s/" % username


def pin_it_button(dst_url, media, description="", label="Pin It",
                  count='none'):
    pin_url = pin_it_url(dst_url, media, description)
    return tags.link_to(label, pin_url, **{'class': 'pin-it-button',
                                           'count-layout': count})


def pinterest_follow_button(username, style='pinterest'):
    cdn_url = "http://passets-cdn.pinterest.com/images/"
    basic_styles = {
        "follow": (cdn_url + "follow-on-pinterest-button.png", 156, 26),
        "pinterest": (cdn_url + "pinterest-button.png", 78, 26),
        "big-p": (cdn_url + "big-p-button.png", 61, 61),
        "small-p": (cdn_url + "small-p-button.png", 16, 16)
    }

    button_style = basic_styles.get(style, style)
    return tags.link_to(tags.image(button_style[0],
                                   "Follow Me on Pinterest",
                                   width=button_style[1],
                                   height=button_style[2]),
                        pinterest_follow_url(username))


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
