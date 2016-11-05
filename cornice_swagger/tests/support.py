# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
import logging
import logging.handlers
import weakref

try:
    from unittest2 import TestCase
except ImportError:
    # Maybe we're running in python2.7?
    from unittest import TestCase  # NOQA
