import requests


class ProposalNotFoundException(Exception):
    def __init__(
        self, proposal_id: int, project_name: str, response: requests.Response
    ):
        super().__init__()
        self.proposal_id = proposal_id
        self.project_name = project_name
        self.response = response

    def __str__(self):
        return (
            f"Proposal id {self.proposal_id} for {self.project_name} could not be found "
            f"at url {self.response.url} (error code {self.response.status_code})"
        )
