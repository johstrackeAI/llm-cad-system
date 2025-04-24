from setuptools import setup, find_packages

setup(
    name="cad_system",
    version="0.1.0",
    packages=find_packages(),
    description="A modular Computer-Aided Design (CAD) system implemented in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Project Team",
    author_email="team@example.com",
    url="https://github.com/yourusername/python-cad-system",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: CAD",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "cad-system=cad_system.system:main",
        ],
    },
)
