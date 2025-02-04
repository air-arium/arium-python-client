"""A setuptools based setup module."""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="arium-apac",
    version="1.17.0",
    description="Arium APAC project",
    long_description=long_description,
    url="https://github.com/air-arium/python",
    author="arium",
    author_email="AriumSupport@air-worldwide.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="arium, apac",
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"config": ["*.ini"]},
    packages=find_packages(where="src"),
    python_requires=">=3.12, <3.13",
    install_requires=["requests-oauthlib"],
)
