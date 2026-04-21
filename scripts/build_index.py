import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.rag_index import rebuild_index


if __name__ == "__main__":
    result = rebuild_index()
    print(result)