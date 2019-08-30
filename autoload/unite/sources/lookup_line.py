#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import vim
from lookup import *
from lookup_utils import *
from lookup_filter_grep import *

class LookupLine(Lookup):
    def __init__(self):
        super(LookupLine, self).__init__()
        self.filter = LookupFilterGrep()
        self.name = "line"

    def do_unite_init(self):
        self.is_redraw = True

    def do_gather_candidates(self):
        return self._getLineList(vim.current.buffer)

    def do_format(self, rows):
        return [{
                "word": "{0}:{1} {2}".format(row[0], row[1], row[3]),
                "abbr": "[L] {0}".format(row[3]),
                "kind": "jump_list",
                "action__path": row[0],
                "action__line": row[1],
                "action__col": row[2],
                "action__text":row[3] 
                } for row in rows]

    def _getLineList(self, buffer):
        bufname = os.path.basename(buffer.name)
        return [(bufname, i, 0, line.encode('utf-8', "replace").decode('utf-8', "replace")) for i, line in enumerate(buffer, 1) if line and not line.isspace()]
