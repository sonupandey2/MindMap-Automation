"""
Sample script — always fails.
Prints an error message to stderr and exits with a non-zero code.
"""

import sys

print("Starting sample job...")
print("Error: Something went wrong during processing.", file=sys.stderr)
sys.exit(1)
