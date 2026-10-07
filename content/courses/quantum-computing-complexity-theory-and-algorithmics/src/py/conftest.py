"""Make each topic package importable by plain module name (import sim, import graphs, ...)."""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
for _sub in ("algorithmics", "complexity", "quantum"):
    _p = os.path.join(_here, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)
