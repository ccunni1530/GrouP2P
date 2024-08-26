from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="group2p",
    version="0.3.1",
    license="MIT",
    project_url={
        "Repository": "https://github.com/ccunni1530/GrouP2P/"
        },
    packages=find_packages(),
    requires=[
        "requests"
        ],
    description="A wrapper for communicating between clients via GroupMe.",
    long_description=description,
    long_description_content_type="text/markdown"
)