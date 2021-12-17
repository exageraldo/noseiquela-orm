from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="noseiquela_orm",
    version="0.0.7-dev2",
    install_requires=[
        "python-dateutil~=2.8",
        "google-cloud-datastore~=2.3",
        "google-auth~=2.3",
    ]
)
