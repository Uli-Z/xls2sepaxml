from setuptools import setup, find_packages

setup(
    name="xls2sepaxml",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "openpyxl",
        "sepaxml",
        "schwifty",
        "flask",
    ],
    entry_points={
        "console_scripts": [
            "xls2sepa-web=xls2sepaxml.web:main",
        ],
    },
    author="Ulrich Zorn",
    license="MIT",
    description="A web-based tool to convert Excel files to SEPA XML transfers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="sepa xml excel converter banking",
    url="https://github.com/uzorn/xls2sepaxml",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
