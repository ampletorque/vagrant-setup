from six.moves.urllib.parse import urlencode


def twitter_tweet_url(text, url, via):
    """
    Return a URL that serves a tweet dialog box for the supplied content.

    :param text: Text to fill in as a default tweet.
    :type text: str
    :param url: URL of the content to link to in the tweet.
    :type url: str, URL
    :param via: A username to mention in the tweet.
    :type via: str, Twitter username
    :returns: URL
    :rtype: str
    """
    text = text.encode('ascii', 'ignore')
    return 'https://twitter.com/intent/tweet?%s' % (
        urlencode(dict(text=text, via=via, url=url)))


def facebook_share_url(text, url, name, caption, image_url, app_id,
                       redirect_uri):
    """
    Return a URL that serves a Facebook share dialog box for the supplied
    content.

    :param text: Text to fill in as a default post.
    :type text: str
    :param url: URL of the content to link to in the post.
    :type url: str, URL
    :param name: Name of the content
    :type name: str
    :param caption: Image caption
    :type caption: str
    :param image_url: URL to an image to use as the post thumbnail
    :type image_url: str, URL
    :param app_id: Facebook app ID
    :type app_id: int
    :param redirect_uri: URL to redirect to after posting
    :type redirect_uri: str, URL
    :returns: URL
    :rtype: str
    """
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
    """
    Return a URL that serves a Pinterest pin dialog box for the supplied
    content.

    :param dst_url: Page to link to in the pin
    :type dst_url: str, URL
    :param media: URL of an image to pin
    :type media: str, URL
    :param description: Default description to use for the pin
    :type description: str
    :returns: URL
    :rtype: str
    """
    # XXX Pinterest doesn't seem to want to use https for this right now, but
    # check back later.
    return "http://pinterest.com/pin/create/button/?%s" % (
        urlencode(dict(url=dst_url, media=media, description=description)))


def gplus_share_url(url):
    """
    Returns a URL that serves a Google+ share dialog box for the supplied
    content.

    :param url: Content to share
    :type url: str, URL
    :returns: URL
    :rtype: str
    """
    return 'https://plus.google.com/share?%s' % (
        urlencode(dict(url=url)))


def project_facebook_url(request, project,
                         description='Check out this Crowd Supply project'):
    """
    Return an appropriately-prepared Facebook share URL for a Project instance.
    """
    return facebook_share_url(
        text=project.teaser,
        url=request.node_url(project),
        name=project.name,
        caption=description,
        image_url=project.img_url(request, 'project-main'),
        app_id=request.registry.settings['facebook.app_id'],
        redirect_uri=request.url)


def project_twitter_url(request, project,
                        description='Check out this Crowd Supply project'):
    """
    Return an appropriately-prepared Twitter tweet URL for a Project instance.
    """
    return twitter_tweet_url(
        text=description,
        via='crowd_supply',
        url=request.node_url(project))


def project_pin_it_url(request, project,
                       description='Check out this Crowd Supply project'):
    """
    Return an appropriately-prepared Pinterest pin URL for a Project instance.
    """
    # XXX Consider adding 'pinset' support to this.
    return pin_it_url(
        dst_url=request.node_url(project),
        media=request.route_url('pinset', id=project.id),
        description=description,
    )
