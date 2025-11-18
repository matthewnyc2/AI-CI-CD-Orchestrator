"""
Setup configuration for AI-CI-CD-Orchestrator package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the version from the orchestrator package
version_file = Path(__file__).parent / "orchestrator" / "__init__.py"
version = None
with open(version_file, "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

if version is None:
    raise ValueError("Could not find version in orchestrator/__init__.py")

# Read the long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        install_requires = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="ai-ci-cd-orchestrator",
    version=version,
    author="AI-CI-CD Team",
    description="A fully autonomous CI/CD system driven by AI that monitors code changes, runs builds and tests, detects failures, and applies fixes using LLMs, ensuring zero-downtime deployments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewnyc2/AI-CI-CD-Orchestrator",
    project_urls={
        "Bug Tracker": "https://github.com/matthewnyc2/AI-CI-CD-Orchestrator/issues",
        "Documentation": "https://github.com/matthewnyc2/AI-CI-CD-Orchestrator/tree/main/docs",
        "Source Code": "https://github.com/matthewnyc2/AI-CI-CD-Orchestrator",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "ai-orchestrator=orchestrator.core.orchestrator:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
