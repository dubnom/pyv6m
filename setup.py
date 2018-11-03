import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvm6",
    version="0.0.1",
    author="Michael Dubno",
    author_email="michael@dubno.com",
    description="VM6 relay controller over Ethernet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dubnom/pyvm6",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
