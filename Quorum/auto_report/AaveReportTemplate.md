# Proposal <proposal_id>. <proposal_title>

### Voting Link
[Link to voting page](<voting_link>)

### Governance Forum Discussions
[Link to forum discussions](<gov_forum_link>)

### Payloads
<loop:chain,payload_link> * <chain> - [proposal payloads](<payload_link>) </loop>


## Certora Analysis

### Proposal Types
{**TODO: Choose types from the following list.**}
* :scroll: :small_red_triangle: Contract upgrades
* :moneybag: :receipt: Asset transfers
* :handshake: Permission granting and revoking
* :wrench: :bar_chart: Configuration updates
* :gem: :new: Listing new assets

### Context
{**TODO: Write context.**}

### Proposal Creation
Transaction: [<transaction_hash>](<transaction_link>)
```
<transaction_data>
```

**`createProposal()` Parameters**
```
<createProposal_parameters_data>
```

### Aave Seatbelt Report

**Proposal Report**
[Link to Seatbelt proposal report](<seatbelt_link>)

**Payload Reports**
<loop:chain,payload_seatbelt_link> * <chain> - [payload Seatbelt report](<payload_seatbelt_link>) </loop>

### Technical Analysis
{**TODO: Write technical analysis.**}

The proposal is consistent with the description on both Snapshot and the governance forum.

### Certora validations
* :white_check_mark: The code on the proposal payload corresponds to the proposal specification.
* :white_check_mark: The proposal includes a proper tests suite, checking all necessary post-conditions.
* :white_check_mark: BGD reviewed the payload before the proposal was submitted.
* :white_check_mark: Certora reviewed the procedure followed to submit the proposal.