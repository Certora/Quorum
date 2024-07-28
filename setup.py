from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name="ProposalsTool",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "proposaltools=ProposalTools.main:main",  # Replace with the actual path to your main function
        ],
    },
    include_package_data=True,
)
