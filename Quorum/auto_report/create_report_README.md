# Auto Report Generation
This tool automatically fetches data from Aave Governance and generates a report automatically using an editable template. To let the generator know where to use the different data tags can be used in the template.

## Tags
To embed data in different places in the template use a tag for that specific data.

### Syntax
To specify a tag type `<tag_name>` where that data should be placed. List of available tags (for different data) is found below.

### Example
For example, given the following template:
```
# Proposal <proposal_id>. <proposal_title>
```
and `proposal_id = 3`, `proposal_title = "I am a proposal"`

The generated report will be:
```
# Proposal 3. I am a proposal
```

## Loop Command
The template also has a special loop command for looping a specific section of the template several times for different values. The loop command works with tags that has a list of values and not a single value. The loop command will multiply the specified template section for each of the values of the tags looped over. Multiple tags can be looped together but they must have the same number of values in them at all times.

### Syntax
To specify a loop command use `<loop:tag1,tag2,...tagn> specified section to loop </loop>`

### Example
Given the following report:
```
List of chaines and their symbols:
<loop:chains,symbols> * <chains>: <symbols> \n <loop>
```
and `chains = ["Bitcoin", "Ethereum", "Solana"]` `symbols = ["BTC", "ETH", "SOL"]`

The generated report will be:
```
List of chaines and their symbols:
* Bitcoin: BTC
* Ethereum: ETH
* Solana: SOL
```

## Available Tags
### Aave
#### Single Value Tags
* `<proposal_id>` - The proposal id.
* `<title>` - The proposal title.
* `<voting_link>` - The link to the voting page.
* `<gov_forum_link>` - The link to the governance forum discussions.
* `<transaction_link>` - Link to the transaction of the proposal creation.
* `<transaction_data>` - The proposal data in the transaction.
* `<createProposal_parameters_data>` - The parameters in `createProposal()`.
* `<seatbelt_link>` - Link to proposal Seatbelt report.

#### List Values Tags
* `<chain>` - The chain of each payload in the proposal.
* `<payload_link>` - List of links to the different payloads.
* `<payload_seatbelt_link>` - List of Seatbelt report of each payload.
