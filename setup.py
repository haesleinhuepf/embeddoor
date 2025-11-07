"""Setup configuration for embeddoor."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="embeddoor",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A browser-based embedding visualization and analysis tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/embeddoor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.14.0",
        "scikit-learn>=1.3.0",
        "pyarrow>=12.0.0",  # For parquet support
        "umap-learn>=0.5.3",
        "pillow>=9.5.0",
        "wordcloud>=1.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
        ],
        "embeddings": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "sentence-transformers>=2.2.2",
            "openai>=1.0.0",
            "google-generativeai>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "embeddoor=embeddoor.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "embeddoor": ["static/*", "templates/*"],
    },
)
