import setuptools
from qop import __version__, __author__


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="qop",
    version=__version__,
    author=__author__,
    author_email="refraction-ray@protonmail.com",
    description="Make quantum operators and algebras native in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/refraction-ray/qop",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["numpy"],
    tests_require=["pytest"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
