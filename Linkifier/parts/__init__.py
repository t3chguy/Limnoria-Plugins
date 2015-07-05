#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os
import glob

list = []
for f in glob.glob(os.path.dirname(__file__)+"/*.py"):
    if os.path.isfile(f) and not os.path.basename(f).startswith('_'):
        part = os.path.basename(f)[:-3]
        list.append(__import__('Linkifier.parts.%s' % part,
                    globals={"__name__": __name__}, fromlist=[part]))
