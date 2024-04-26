import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, "src", "deconfig", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

if "DEV_VERSION_SUFFIX" in os.environ:
    about["__version__"] += os.environ["DEV_VERSION_SUFFIX"]

setup(
    version=about["__version__"],
    packages=["deconfig"],
    package_dir={"": "src"},
    package_data={"": ["LICENSE", "README.md"]},
    include_package_data=True,
)
