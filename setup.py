from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requirements = ["plotly==4.1.1", "psutil==5.6.3", "six==1.12.0", "retrying==1.3.3"]

setup(
    name="metrace",
    version="1.0.1",
    author="sloev",
    author_email="johannes.valbjorn@gmail.com",
    url="https://github.com/sloev/metrace",
    description="cpu and memory tracing for process trees",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["metrace"],
    package_dir={"metrace": "metrace"},
    entry_points={"console_scripts": ["metrace=metrace.cli:cli"]},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords="metrace cpu memory trace",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
