from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()
    
def read_version() -> str:
    with open('version') as f:
        return f.read()

setup(
    name="Quorum",
    version=read_version(),
    packages=find_packages(),
    install_requires=read_requirements(),
    include_package_data=True,
        package_data={
        '': ['repos.json'],
    },
    entry_points={
        "console_scripts": [
            "CheckProposal=Quorum.check_proposal:main",
        ],
    },
)
