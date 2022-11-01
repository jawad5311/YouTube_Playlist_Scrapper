from setuptools import setup, find_packages

setup(
    name='yt_scrapper',
    version='0.0.1',
    description='Scrape YouTube channel and videos data using YouTube API v3',
    author='Muhammad Jawad',
    license='MIT',
    keywords='youtube',
    packages=find_packages(),
    install_requires=[
        'pandas',
    ]
)
