import pytest


from Quorum.apis.block_explorers.source_code import SourceCode
from Quorum.checks.price_feed import PriceFeedCheck
from Quorum.utils.chain_enum import Chain
from Quorum.apis.price_feeds import ChainLinkAPI

from pathlib import Path


@pytest.mark.parametrize('source_codes', ['ETH/0xAD6c03BF78A3Ee799b86De5aCE32Bb116eD24637'], indirect=True)
def test_price_feed(source_codes: list[SourceCode], tmp_output_path: Path):
    price_feed_check = PriceFeedCheck('Aave', Chain.ETH, '', source_codes, [
        ChainLinkAPI()], [])
    price_feed_check.verify_price_feed()

    assert sorted([p.name for p in price_feed_check.check_folder.iterdir()]) == ['AaveV2Ethereum']


def test_source_code_clean():
    code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IProposalGenericExecutor} from 'aave-helpers/interfaces/IProposalGenericExecutor.sol';
import {AaveV2Ethereum, AaveV2EthereumAssets, ILendingPoolConfigurator} from 'aave-address-book/AaveV2Ethereum.sol';

/**
 * @title Reserve Factor Updates Mid July
 * @author karpatkey_TokenLogic
 * - Snapshot: https://snapshot.org/#/aave.eth/proposal/0x9cc7906f04f45cebeaa48a05ed281f49da00d89c4dd988a968272fa179f14d06
 * - Discussion: https://governance.aave.com/t/arfc-increase-bridged-usdc-reserve-factor-across-all-deployments/17787
 */
contract AaveV2Ethereum_ReserveFactorUpdatesMidJuly_20240711 is IProposalGenericExecutor {
  ILendingPoolConfigurator public constant POOL_CONFIGURATOR =
    ILendingPoolConfigurator(AaveV2Ethereum.POOL_CONFIGURATOR);

  uint256 public constant DAI_RF = 65_00;
  uint256 public constant LINK_RF = 70_00;
  uint256 public constant USDC_RF = 65_00;
  uint256 public constant USDT_RF = 65_00;
  uint256 public constant WBTC_RF = 70_00;
  uint256 public constant WETH_RF = 65_00;

  function execute() external {
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.DAI_UNDERLYING, DAI_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.LINK_UNDERLYING, LINK_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.USDC_UNDERLYING, USDC_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.USDT_UNDERLYING, USDT_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.WBTC_UNDERLYING, WBTC_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.WETH_UNDERLYING, WETH_RF);
  }
}
    """
    cleaned = PriceFeedCheck.remove_solidity_comments(code)
    expected = """pragma solidity ^0.8.0;

import {IProposalGenericExecutor} from 'aave-helpers/interfaces/IProposalGenericExecutor.sol';
import {AaveV2Ethereum, AaveV2EthereumAssets, ILendingPoolConfigurator} from 'aave-address-book/AaveV2Ethereum.sol';


contract AaveV2Ethereum_ReserveFactorUpdatesMidJuly_20240711 is IProposalGenericExecutor {
  ILendingPoolConfigurator public constant POOL_CONFIGURATOR =
    ILendingPoolConfigurator(AaveV2Ethereum.POOL_CONFIGURATOR);

  uint256 public constant DAI_RF = 65_00;
  uint256 public constant LINK_RF = 70_00;
  uint256 public constant USDC_RF = 65_00;
  uint256 public constant USDT_RF = 65_00;
  uint256 public constant WBTC_RF = 70_00;
  uint256 public constant WETH_RF = 65_00;

  function execute() external {
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.DAI_UNDERLYING, DAI_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.LINK_UNDERLYING, LINK_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.USDC_UNDERLYING, USDC_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.USDT_UNDERLYING, USDT_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.WBTC_UNDERLYING, WBTC_RF);
    POOL_CONFIGURATOR.setReserveFactor(AaveV2EthereumAssets.WETH_UNDERLYING, WETH_RF);
  }
}"""
    # Strip leading/trailing whitespace for accurate comparison
    assert cleaned.strip() == expected.strip()
