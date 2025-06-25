from quorum.apis.block_explorers.chains_api import Chain, ChainAPI


def test_get_complete_contract_analysis():
    """
    Test the get_complete_contract_analysis method of ChainAPI for a specific Ethereum contract.

    This test validates that the method correctly retrieves:
    1. Runtime bytecode
    2. Constructor arguments

    Based on the notebook analysis of contract 0x91924f1486b9c5b4c2f4e494fe3162225fa2cd94
    """
    # Test contract address from the notebook
    address = "0x91924f1486b9c5b4c2f4e494fe3162225fa2cd94"

    # Expected values from the notebook
    test_runtime_bytecode = "0x6080604052600436106100615763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416638568523a81146100d85780638da5cb5b146100fc578063b76ea9621461012d578063f2fde38b14610187575b60008054604051600160a060020a039091169134919081818185875af192505050156100d157600054604080513481529051600160a060020a039092169133917f5548c837ab068cf56a2c2479df0882a4922fd203edb7517321831d95078c5f62919081900360200190a36100d6565b600080fd5b005b3480156100e457600080fd5b506100d6600160a060020a03600435166024356101a8565b34801561010857600080fd5b50610111610244565b60408051600160a060020a039092168252519081900360200190f35b60408051602060046024803582810135601f81018590048502860185019096528585526100d6958335600160a060020a03169536956044949193909101919081908401838280828437509497506102539650505050505050565b34801561019357600080fd5b506100d6600160a060020a03600435166102f1565b600054600160a060020a031633146101bf57600080fd5b60008054604080517fa9059cbb000000000000000000000000000000000000000000000000000000008152600160a060020a0392831660048201526024810185905290519185169263a9059cbb9260448084019382900301818387803b15801561022857600080fd5b505af115801561023c573d6000803e3d6000fd5b505050505050565b600054600160a060020a031681565b600054600160a060020a0316331461026a57600080fd5b81600160a060020a0316348260405180828051906020019080838360005b838110156102a0578181015183820152602001610288565b50505050905090810190601f1680156102cd5780820380516001836020036101000a031916815260200191505b5091505060006040518083038185875af19250505015156102ed57600080fd5b5050565b600054600160a060020a0316331461030857600080fd5b61031181610314565b50565b600160a060020a038116151561032957600080fd5b60008054604051600160a060020a03808516939216917f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e091a36000805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a03929092169190911790555600a165627a7a72305820c37bc7c62ebfe71a7f833b31d62e1e40a334cb9ec88b607dcd2fa3e663cac5d10029"
    test_constructor_args = (
        "0x00000000000000000000000055fe002aeff02f77364de339a1292923a15844b8"
    )

    # Create ChainAPI instance for Ethereum
    api = ChainAPI(Chain.ETH)

    # Perform the complete contract analysis
    analysis = api.get_complete_contract_analysis(address)

    # Assertions
    assert analysis is not None, "Analysis should not be None"

    # Test runtime bytecode matches expected value
    assert (
        analysis.runtime_bytecode == test_runtime_bytecode
    ), f"Runtime bytecode mismatch. Expected: {test_runtime_bytecode}, Got: {analysis.runtime_bytecode}"

    # Test constructor arguments match expected value
    assert (
        analysis.constructor_args == test_constructor_args
    ), f"Constructor args mismatch. Expected: {test_constructor_args}, Got: {analysis.constructor_args}"

    # Additional validations
    assert analysis.has_runtime_bytecode(), "Should have runtime bytecode"
    assert analysis.has_constructor_args(), "Should have constructor arguments"
    assert (
        not analysis.has_errors()
    ), f"Should not have errors, but got: {analysis.errors}"


def test_get_complete_contract_analysis_properties():
    """
    Test additional properties and methods of the ContractAnalysisResult.

    This test ensures the helper methods work correctly for the contract analysis.
    """
    address = "0x91924f1486b9c5b4c2f4e494fe3162225fa2cd94"
    api = ChainAPI(Chain.ETH)
    analysis = api.get_complete_contract_analysis(address)

    # Test helper methods
    assert isinstance(
        analysis.runtime_bytecode, str
    ), "Runtime bytecode should be a string"
    assert isinstance(
        analysis.constructor_args, str
    ), "Constructor args should be a string"
    assert isinstance(analysis.errors, list), "Errors should be a list"

    # Test that bytecode starts with 0x
    assert analysis.runtime_bytecode.startswith(
        "0x"
    ), "Runtime bytecode should start with 0x"
    assert analysis.constructor_args.startswith(
        "0x"
    ), "Constructor args should start with 0x"

    # Test length validations (bytecode should be substantial)
    assert len(analysis.runtime_bytecode) > 10, "Runtime bytecode should be substantial"
    assert (
        len(analysis.constructor_args) > 2
    ), "Constructor args should have content beyond 0x"
