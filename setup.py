from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name="ProposalTools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=read_requirements(),
    include_package_data=True,
        package_data={
        '': ['repos.json'],
    },
    entry_points={
        "console_scripts": [
            "CheckProposal=ProposalTools.main:main",  # Replace with the actual path to your main function
        ],
    },
)
