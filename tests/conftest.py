import os
import sys

# Import the project modules from the repository root, and never start the
# server's UDP threads during tests.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SERVER_START_THREADS", "0")
