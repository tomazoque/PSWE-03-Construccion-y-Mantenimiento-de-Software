import os
import sys

# Ensure tests can import modules from the Caso1 folder
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CASO1_PATH = os.path.join(ROOT, "Caso1")
if CASO1_PATH not in sys.path:
    sys.path.insert(0, CASO1_PATH)
