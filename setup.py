import setuptools
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yt_scrapper",
    version="0.0.6",
    author="Muhammad Jawad",
    author_email="muhammadjawad5311@gmail.com",
    description="Download YouTube data using YouTube API v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jawad5311/YouTube_Scrapper",
    project_urls={
        "Bug Tracker": "https://github.com/jawad5311/YouTube_Scrapper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    package_dir={'':"src"},
    packages=find_packages("src"),
    python_requires=">=3.7",)