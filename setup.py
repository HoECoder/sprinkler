"""Setup configuration"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()  # pylint: disable=invalid-name

setuptools.setup(
    name="sprinkler",
    version="0.0.1a",
    author="James P Hansen",
    author_email="jphansen@gmail.com",
    description="Sprinkler driver for OSPi Board",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=["test", "build"]),
    install_requires=[
        'click',
        'pendulum',
        'marshmallow'
    ],
    entry_points={
        'console_scripts': [
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
