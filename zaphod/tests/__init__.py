from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import warnings
from sqlalchemy.exc import SAWarning

# Filter out pysqlite Decimal loss of precision warning.
warnings.filterwarnings(
    'ignore', '.*pysqlite does \*not\* support Decimal', SAWarning)
