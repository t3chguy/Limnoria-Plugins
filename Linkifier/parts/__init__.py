#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import glob

__all__ = []
for f in glob.glob(os.path.dirname(__file__)+"/*.py"):
    if os.path.isfile(f) and not os.path.basename(f).startswith('_'):
        __all__.append(os.path.basename(f)[:-3])

list    = []
for part in __all__:
	list.append(__import__('Linkifier.parts.%s' % part,
	             globals={"__name__": __name__}, fromlist=[part]))