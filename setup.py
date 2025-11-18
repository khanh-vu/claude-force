"""
Setup configuration for claude-force package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#") and not line.startswith("pytest")
    ]

setup(
    name="claude-force",
    version="1.2.3",
    author="Claude Force Team",
    author_email="",
    description="Multi-Agent Orchestration System for Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khanh-vu/claude-force",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "claude-force=claude_force.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "claude_force": ["py.typed"],
    },
    options={
        'metadata': {
            'license_files': []
        }
    },
    keywords="claude anthropic ai agents multi-agent orchestration",
    project_urls={
        "Bug Reports": "https://github.com/khanh-vu/claude-force/issues",
        "Source": "https://github.com/khanh-vu/claude-force",
        "Documentation": "https://github.com/khanh-vu/claude-force/blob/main/README.md",
    },
)
