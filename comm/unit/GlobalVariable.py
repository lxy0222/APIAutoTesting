import threading
from types import SimpleNamespace


class GlobalData:
    local_data = threading.local()
    local_data.namespace = SimpleNamespace()

