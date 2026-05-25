import sys
from pathlib import Path

# Bootstrap project root to allow executing as a direct script
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.cli.main import main

if __name__ == "__main__":
    main()