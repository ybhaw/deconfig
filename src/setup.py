import os
from setuptools import setup, find_packages

import deconfig
dev_version = os.environ.get("DEV_VERSION")

print(find_packages())

setup(
    version=dev_version or deconfig.__version__,
    packages=find_packages(),
    package_dir={"deconfig": "deconfig"},
)
