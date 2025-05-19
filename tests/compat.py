from __future__ import annotations

import sys

if sys.version_info >= (3, 10):
    aiter = aiter  # noqa: F821
    anext = anext  # noqa: F821
else:

    def aiter(obj):
        return obj.__aiter__()

    def anext(obj):
        return obj.__anext__()
