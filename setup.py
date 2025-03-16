"""Setup script for warp-theme-creator."""

from setuptools import setup, find_packages
from warp_theme_creator import __version__

setup(
    name="warp-theme-creator",
    version=__version__,
    description="Generate Warp terminal themes from website colors",
    author="David Parker",
    author_email="davidparkercodes@example.com",
    url="https://github.com/davidparkercodes/warp-theme-creator",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "warp-theme-creator=warp_theme_creator.main:main",
        ],
    },
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "cssutils>=2.3.0",
        "Pillow>=8.0.0",
        "colorthief>=0.2.1",
        "PyYAML>=6.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)