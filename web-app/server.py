import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("p5r_root_server", str(ROOT / "server.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

for _n in dir(mod):
    if not _n.startswith("_"):
        globals()[_n] = getattr(mod, _n)

if __name__ == "__main__":
    main()
