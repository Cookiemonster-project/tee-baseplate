from setuptools import setup, find_packages

setup(
    name="teebase",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author="Suika",
    author_email="suika8156@gmail.com",
    description="A baseplate for tee",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)