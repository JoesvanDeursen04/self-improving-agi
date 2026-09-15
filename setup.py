from setuptools import setup, find_packages

setup(
    name="self-improving-agi",
    version="0.1.0",
    description="Complete implementation of a self-improving, conscious AGI system",
    author="Joes van Deursen",
    author_email="joes@example.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
        "networkx>=3.1",
        "pandas>=2.0.0",
        "loguru>=0.7.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "z3-solver>=4.12.0",
        "torch>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "agi-start=integration.agi_system:main",
        ],
    },
)
