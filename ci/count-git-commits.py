"""
Print the number of commits in the current git branch.
"""

import subprocess

subprocess.run(['git', 'rev-list', 'HEAD', '--count'], check=True)
