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
        '': ['ground_truth.json', "*j2"],        
    },
    entry_points={
        "console_scripts": [
            "CheckProposal=Quorum.entry_points.check_proposal:main",
            "IPFSValidator=Quorum.entry_points.ipfs_validator:main",
            "CreateReport=Quorum.entry_points.create_report:main",
            "SetupQuorum=Quorum.entry_points.setup_quorum:main",
        ],
    },
)
