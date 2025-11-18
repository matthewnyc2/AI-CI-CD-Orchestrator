"""Setup configuration for AI-CI-CD-Orchestrator package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ai-cicd-orchestrator",
    version="0.1.0",
    author="AI-CICD Team",
    author_email="team@example.com",
    description="A fully autonomous CI/CD system driven by AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewnyc2/AI-CI-CD-Orchestrator",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.28.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "GitPython>=3.1.0",
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "httpx>=0.24.0",
        "structlog>=23.0.0",
        "colorlog>=6.7.0",
        "slack-sdk>=3.21.0",
        "aiofiles>=23.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.11.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dateutil>=2.8.0",
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-cicd=orchestrator.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "orchestrator": ["py.typed"],
    },
    zip_safe=False,
)
