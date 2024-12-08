class AaveTags:
    def __init__(self, proposal_id: int) -> None:
        self.proposal_id = proposal_id
        self.tag_mappings = {
            'proposal_id': str(proposal_id),
            'proposal_title': self.get_proposal_title(),
            'chain': self.get_chains(),
            'payload_link': self.get_payload_links(),
            'transaction_hash': self.get_transaction_hash(),
            'transaction_data': self.get_transaction_data(),
            'createProposal_parameters_data': self.get_create_func_parameters_data(),
            'seatbelt_link': self.get_seatbelt_link(),
            'payload_seatbelt_link': self.get_seatbelt_payload_links()
        }

    def get_proposal_title(self) -> str:
        return 'titular'

    def get_chains(self) -> list[str]:
        return ['btc', 'eth', 'sol']


    def get_payload_links(self) -> list[str]:
        return ['btc_link', 'eth_link', 'sol_link']


    def get_transaction_hash(self) -> str:
        return 'hush baby'


    def get_transaction_link(self) -> str:
        return 'www.transaction.link.com'


    def get_transaction_data(self) -> str:
        return ('Some transaction data \n'
                'Like this \n'
                'And this')


    def get_create_func_parameters_data(self) -> str:
        return ('A\n'
                'long\n'
                'list\n'
                'of\n'
                'parameters\n'
                'data')


    def get_seatbelt_link(self) -> str:
        return 'www.seatbelt.com'


    def get_seatbelt_payload_links(self) -> list[str]:
        return ['www.seatbelt.btc', 'www.seatbelt.eth', 'www.seatbelt.sol']