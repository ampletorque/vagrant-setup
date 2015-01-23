from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from string import Template

from six.moves import range

from webhelpers2.html import HTML, literal


class PagerPiece(object):
    """
    An element of a pager, as yielded by an iterator method of ``Pager``.

    ellipsis
        True if this element is an ellipsis (a gap between pages), False
        otherwise.

    active
        True if this element is the currently active page, False otherwise.

    number
        The page number referenced by this element. None if this piece is an
        ellipsis.

    url
        The URL for the page referenced by this element. None if this piece is
        an ellipsis, but provided for the active page.
    """
    def __init__(self, number, url, ellipsis, active):
        self.number = number
        self.url = url
        self.ellipsis = ellipsis
        self.active = active


class Page(list):
    """
    A handle for making pagination widgets, pagers, etc. Essentially,
    represents a page of a collection.

    item_count
        NUmber of items in the collection

    page
        Index of the current page

    items_per_page
        Max items on a page (None for no max, which means all on one page)

    page_count
        Number of pages

    previous_page
        Number of the previous page, or None if this is the first page

    next_page
        Number of the next page, or None if this is the last page

    previous_url
        URL of the previous page, or None

    next_url
        URL of the next page, or None

    first_item
        Index of the first item on this page

    last_item
        Index of the last item on this page
    """
    def __init__(self, request, collection,
                 page, items_per_page, item_count, page_param='page',
                 presliced_list=False):
        self.request = request

        self.page_param = page_param

        self.page = page
        self.items_per_page = items_per_page or item_count
        self.item_count = item_count

        if self.item_count:
            self.first_page = 1
            self.page_count = ((self.item_count - 1) // items_per_page) + 1
            self.last_page = self.first_page + self.page_count - 1

            self.previous_page = (page - 1) if page > 1 else None
            self.next_page = (page + 1) if page < self.page_count else None
            self.first_item = (page - 1) * items_per_page + 1
            self.last_item = min(self.first_item + items_per_page - 1,
                                 item_count)

            if presliced_list:
                self.sliced_collection = collection
            else:
                first = self.first_item - 1
                last = self.last_item
                self.sliced_collection = list(collection[first:last])
        else:
            self.first_page = None
            self.page_count = 0
            self.last_page = None

            self.previous_page = None
            self.next_page = None
            self.first_item = None
            self.last_item = None

            self.sliced_collection = []

        list.__init__(self, self.sliced_collection)

    def page_url(self, new_page):
        """
        Return the URL for a particular page number.
        """
        if new_page == 1:
            query = {self.page_param: None}
        else:
            query = {self.page_param: new_page}
        return self.request.current_path_with_params(**query)

    @property
    def previous_url(self):
        if self.previous_page:
            return self.page_url(self.previous_page)

    @property
    def next_url(self):
        if self.next_page:
            return self.page_url(self.next_page)

    def iter_radius(self, radius):
        """
        Yield a sequence of ``PagerPiece`` instances to create a pagination
        widget with radius ``radius`` around the current page.

        E.g. for a 12-page collection:

        radius of 2 at page 5
            1 .. 3 4 [5] 6 7 .. 12

        radius of 2 at page 4
            1 2 3 [4] 5 6 .. 12

        radius of 2 at page 3
            1 2 [3] 4 5 .. 12

        radius of 2 at page 10
            1 .. 8 9 [10] 11 12

        radius of 2 at page 9
            1 .. 7 8 [9] 10 11 12

        radius of 2 at page 8
            1 .. 6 7 [8] 9 10 .. 12
        """
        # First yield the first page
        yield PagerPiece(number=1,
                         url=self.page_url(1),
                         ellipsis=False,
                         active=(self.page == 1))

        # Then maybe yield ellipsis
        if self.page > (radius + 2):
            yield PagerPiece(number=None,
                             url=None,
                             ellipsis=True,
                             active=False)

        # Then yield radius pages
        for page in range(self.page - radius, self.page + radius + 1):
            if 1 < page < self.page_count:
                yield PagerPiece(number=page,
                                 url=self.page_url(page),
                                 ellipsis=False,
                                 active=(page == self.page))

        # Then maybe yield ellipsis
        if self.page < (self.page_count - 1 - radius):
            yield PagerPiece(number=None,
                             url=None,
                             ellipsis=True,
                             active=False)

        # Then maybe yield the last page
        if self.page_count > 1:
            yield PagerPiece(number=self.page_count,
                             url=self.page_url(self.page_count),
                             ellipsis=False,
                             active=(self.page == self.page_count))

    def pager(self, format='~2~', page_param='page',
              show_if_single_page=False, separator=' ',
              symbol_first='<<', symbol_last='>>',
              symbol_previous='<', symbol_next='>',
              link_attr={'class': 'pager_link'},
              curpage_attr={'class': 'pager_curpage'},
              dotdot_attr={'class': 'pager_dotdot'}, **kwargs):
        """
        Return string with links to other pages (e.g. "1 2 [3] 4 5 6 7").

        format:
            Format string that defines how the pager is rendered. The string
            can contain the following $-tokens that are substituted by the
            string.Template module:

            - $first_page: number of first reachable page
            - $last_page: number of last reachable page
            - $page: number of currently selected page
            - $page_count: number of reachable pages
            - $items_per_page: maximal number of items per page
            - $first_item: index of first item on the current page
            - $last_item: index of last item on the current page
            - $item_count: total number of items
            - $link_first: link to first page (unless this is first page)
            - $link_last: link to last page (unless this is last page)
            - $link_previous: link to previous page (unless this is first page)
            - $link_next: link to next page (unless this is last page)

            To render a range of pages the token '~3~' can be used. The
            number sets the radius of pages around the current page.
            Example for a range with radius 3:

            '1 .. 5 6 7 [8] 9 10 11 .. 500'

            Default: '~2~'

        symbol_first
            String to be displayed as the text for the %(link_first)s
            link above.

            Default: '<<'

        symbol_last
            String to be displayed as the text for the %(link_last)s
            link above.

            Default: '>>'

        symbol_previous
            String to be displayed as the text for the %(link_previous)s
            link above.

            Default: '<'

        symbol_next
            String to be displayed as the text for the %(link_next)s
            link above.

            Default: '>'

        separator:
            String that is used to separate page links/numbers in the
            above range of pages.

            Default: ' '

        page_param:
            The name of the parameter that will carry the number of the
            page the user just clicked on. The parameter will be passed
            to a url_for() call so if you stay with the default
            ':controller/:action/:id' routing and set page_param='id' then
            the :id part of the URL will be changed. If you set
            page_param='page' then url_for() will make it an extra
            parameters like ':controller/:action/:id?page=1'.
            You need the page_param in your action to determine the page
            number the user wants to see. If you do not specify anything
            else the default will be a parameter called 'page'.

            Note: If you set this argument and are using a URL generator
            callback, the callback must accept this name as an argument instead
            of 'page'.
            callback, becaust the callback requires its argument to be 'page'.
            Instead the callback itself can return any URL necessary.

        show_if_single_page:
            if True the navigator will be shown even if there is only
            one page

            Default: False

        link_attr (optional)
            A dictionary of attributes that get added to A-HREF links
            pointing to other pages. Can be used to define a CSS style
            or class to customize the look of links.

            Example: { 'style':'border: 1px solid green' }

            Default: { 'class':'pager_link' }

        curpage_attr (optional)
            A dictionary of attributes that get added to the current
            page number in the pager (which is obviously not a link).
            If this dictionary is not empty then the elements
            will be wrapped in a SPAN tag with the given attributes.

            Example: { 'style':'border: 3px solid blue' }

            Default: { 'class':'pager_curpage' }

        dotdot_attr (optional)
            A dictionary of attributes that get added to the '..' string
            in the pager (which is obviously not a link). If this
            dictionary is not empty then the elements will be wrapped in
            a SPAN tag with the given attributes.

            Example: { 'style':'color: #808080' }

            Default: { 'class':'pager_dotdot' }

        Additional keyword arguments are used as arguments in the links.
        Otherwise the link will be created with url_for() which points
        to the page you are currently displaying.
        """
        self.curpage_attr = curpage_attr
        self.separator = separator
        self.pager_kwargs = kwargs
        self.page_param = page_param
        self.link_attr = link_attr
        self.dotdot_attr = dotdot_attr

        # Don't show navigator if there is no more than one page
        if self.page_count == 0 or (self.page_count == 1 and
                                    not show_if_single_page):
            return ''

        # Replace ~...~ in token format by range of pages
        result = re.sub(r'~(\d+)~', self._range, format)

        # Interpolate '%' variables
        result = Template(result).safe_substitute({
            'first_page': self.first_page,
            'last_page': self.last_page,
            'page': self.page,
            'page_count': self.page_count,
            'items_per_page': self.items_per_page,
            'first_item': self.first_item,
            'last_item': self.last_item,
            'item_count': self.item_count,
            'link_first': self.page > self.first_page and
            self._pagerlink(self.first_page, symbol_first) or '',
            'link_last': self.page < self.last_page and
            self._pagerlink(self.last_page, symbol_last) or '',
            'link_previous': self.previous_page and
            self._pagerlink(self.previous_page, symbol_previous) or '',
            'link_next': self.next_page and
            self._pagerlink(self.next_page, symbol_next) or ''
        })

        return literal(result)

    def _range(self, regexp_match):
        """
        Return range of linked pages (e.g. '1 2 [3] 4 5 6 7 8').

        Arguments:

        regexp_match
            A "re" (regular expressions) match object containing the
            radius of linked pages around the current page in
            regexp_match.group(1) as a string

        This function is supposed to be called as a callable in
        re.sub.

        """
        radius = int(regexp_match.group(1))

        # Compute the first and last page number within the radius
        # e.g. '1 .. 5 6 [7] 8 9 .. 12'
        # -> leftmost_page  = 5
        # -> rightmost_page = 9
        leftmost_page = max(self.first_page, (self.page - radius))
        rightmost_page = min(self.last_page, (self.page + radius))

        nav_items = []

        # Create a link to the first page (unless we are on the first page
        # or there would be no need to insert '..' spacers)
        if self.page != self.first_page and self.first_page < leftmost_page:
            nav_items.append(self._pagerlink(self.first_page, self.first_page))

        # Insert dots if there are pages between the first page
        # and the currently displayed page range
        if leftmost_page - self.first_page > 1:
            # Wrap in a SPAN tag if nolink_attr is set
            text = '..'
            if self.dotdot_attr:
                text = HTML.span(c=text, **self.dotdot_attr)
            nav_items.append(text)

        for thispage in range(leftmost_page, rightmost_page + 1):
            # Hilight the current page number and do not use a link
            if thispage == self.page:
                text = '%s' % (thispage,)
                # Wrap in a SPAN tag if nolink_attr is set
                if self.curpage_attr:
                    text = HTML.span(c=text, **self.curpage_attr)
                nav_items.append(text)
            # Otherwise create just a link to that page
            else:
                text = '%s' % (thispage,)
                nav_items.append(self._pagerlink(thispage, text))

        # Insert dots if there are pages between the displayed
        # page numbers and the end of the page range
        if self.last_page - rightmost_page > 1:
            text = '..'
            # Wrap in a SPAN tag if nolink_attr is set
            if self.dotdot_attr:
                text = HTML.span(c=text, **self.dotdot_attr)
            nav_items.append(text)

        # Create a link to the very last page (unless we are on the last
        # page or there would be no need to insert '..' spacers)
        if self.page != self.last_page and rightmost_page < self.last_page:
            nav_items.append(self._pagerlink(self.last_page, self.last_page))

        return self.separator.join(nav_items)

    def _pagerlink(self, page, text):
        """
        Create a link tag to another page, with specified text.

        page
            Number of the page that the link points to

        text
            Text to be printed in the <a> tag
        """
        link_url = self.page_url(page)
        return HTML.a(text, href=link_url, **self.link_attr)
