from __future__ import (absolute_import, division, print_function,
                        unicode_literals)



class BaseReportsView(object):
    def __init__(self, request):
        self.request = request
