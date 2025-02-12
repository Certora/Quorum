from quorum.apis.multisig.safe_api import SafeAPI


def test_safe_api():
    api = SafeAPI()
    multisig = api.get_multisig_info("0xA1c93D2687f7014Aaf588c764E3Ce80aF016229b")
    assert multisig.owners == [
        "0x320A4e54e3641A7a9dAF47016a93CDe6F848A340",
        "0xb647055A9915bF9c8021a684E175A353525b9890",
        "0x6efa225841090Fb54d7bCE4593c700C0f24C4be8",
        "0x329c54289Ff5D6B7b7daE13592C6B1EDA1543eD4",
        "0x009d13E9bEC94Bf16791098CE4E5C168D27A9f07",
    ]
    assert multisig.threshold == 3
    assert multisig.address == "0xA1c93D2687f7014Aaf588c764E3Ce80aF016229b"


def test_non_multisig():
    api = SafeAPI()
    non_multisig = api.get_multisig_info("0x0000000000000000000000000000000000000000")
    assert non_multisig is None
