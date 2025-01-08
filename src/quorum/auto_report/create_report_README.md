# Auto Report Generation
This tool automatically fetches data from Aave Governance and generates a report automatically using an editable template. To let the generator know where to use the different data tags can be used in the template.

The template for the report is using Jinja2: https://jinja.palletsprojects.com/en/stable/templates/

## Available Tags
### Aave
#### Single Value Tags
* `{{ proposal_id }}` - The proposal id.
* `{{ title }}` - The proposal title.
* `{{ voting_link }}` - The link to the voting page.
* `{{ gov_forum_link }}` - The link to the governance forum discussions.
* `{{ transaction_link }}` - Link to the transaction of the proposal creation.
* `{{ creator }}` - Creator of the proposal.
* `{{ access_level }}` - Access level of the proposal.
* `{{ ipfs_hash }}` - The IPFS hash.
* `{{ createProposal_parameters_data }}` - The parameters in `createProposal()`.
* `{{ seatbelt_link }}` - Link to proposal Seatbelt report.

#### List Values Tags
* `{{ chain }}` - The chain of each payload in the proposal.
* `{{ payload_link }}` - List of links to the different payloads.
* `{{ payload_seatbelt_link }}` - List of Seatbelt report of each payload.
