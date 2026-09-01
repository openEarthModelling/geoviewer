import os
import sys
import tempfile
from pathlib import Path

# datashader/numba jit cache must point somewhere writable before geoviews/holoviews
# imports pull datashader in (same workaround as app.py, applied for tests).
os.environ.setdefault("NUMBA_CACHE_DIR", os.path.join(tempfile.gettempdir(), "numba_cache"))

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
