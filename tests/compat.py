from __future__ import annotations

import sys

if sys.version_info >= (3, 10):
    aiter = aiter
    anext = anext
else:

    def aiter(obj):
        return obj.__aiter__()

    def anext(obj):
        return obj.__anext__()
