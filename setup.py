from setuptools import setup, find_packages

setup(
    name="aiosmf",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "flatbuffers>=1.10",
        "xxhash>=1.3.0",
        "zstandard>=0.11.0",
    ],
    author="Noah Watkins",
    author_email="noahwatkins@gmail.com",
    description="Python asyncio smf rpc implementation",
    license="Apache License 2.0",
    keywords="smf rpc",
    url="https://github.com/noahdesu/aiosmf",
)
