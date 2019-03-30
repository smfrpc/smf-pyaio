from setuptools import setup, find_packages

long_description = open("README.md").read()

setup(
    name="aiosmf",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    author="Noah Watkins",
    author_email="noahwatkins@gmail.com",
    description="Python asyncio smf rpc implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="smf rpc seastar",
    url="https://github.com/noahdesu/aiosmf",
    zip_safe=True,
    install_requires=[
        "flatbuffers>=1.10",
        "xxhash>=1.3.0",
        "zstandard>=0.11.0",
    ],
    classifiers = [
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Topic :: System :: Networking",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
    ]
)
