"""
Sample script — accepts and prints command-line arguments.

Usage:
    python sample_arguments.py --name John --environment production
"""

import argparse

parser = argparse.ArgumentParser(description='Sample script with arguments')
parser.add_argument('--name', type=str, default='World', help='Your name')
parser.add_argument('--environment', type=str, default='development', help='Target environment')

args = parser.parse_args()

print(f"Hello, {args.name}!")
print(f"Environment: {args.environment}")
print("Arguments processed successfully.")
