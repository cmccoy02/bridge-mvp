from setuptools import setup, find_packages

setup(
    name="bridge-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "rich",
        "requests",
        "radon",
        "bandit",
        "python-dotenv",
        "pyfiglet",
        "GitPython",
    ],
    entry_points={
        'console_scripts': [
            'bridge = bridge_cli.cli:cli',
        ],
    },
)
