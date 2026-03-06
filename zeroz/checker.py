"""
ZEROZ Checker -- Free Edition (compiled)

Login verification only. Inbox access and OWA features
require the premium version. Join t.me/cosmounion for details.
"""

import base64, zlib, marshal, types, os

_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_DIR, "_checker_blob.dat"), "r") as _f:
    _blob = _f.read()

_code = marshal.loads(zlib.decompress(base64.b85decode(_blob)))
_mod = types.ModuleType("zeroz._engine")
exec(_code, _mod.__dict__)

check_account = _mod.check_account

del _blob, _code, _mod, _f, _DIR
