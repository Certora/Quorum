// AUTOGENERATED - MANUALLY CHANGES WILL BE REVERTED BY THE GENERATOR
// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0;

import {ILendingPoolAddressesProvider, ILendingPool, ILendingPoolConfigurator, IAaveOracle, IAaveProtocolDataProvider, ILendingRateOracle} from './AaveV2.sol';
import {ICollector} from './common/ICollector.sol';
library AaveV2EthereumArc {
  // https://etherscan.io/address/0x6FdfafB66d39cD72CFE7984D3Bbcc76632faAb00
  ILendingPoolAddressesProvider internal constant POOL_ADDRESSES_PROVIDER =
    ILendingPoolAddressesProvider(0x6FdfafB66d39cD72CFE7984D3Bbcc76632faAb00);

  // https://etherscan.io/address/0x37D7306019a38Af123e4b245Eb6C28AF552e0bB0
  ILendingPool internal constant POOL = ILendingPool(0x37D7306019a38Af123e4b245Eb6C28AF552e0bB0);

  // https://etherscan.io/address/0xfbF029508c061B440D0cF7Fd639e77Fb2E196241
  address internal constant POOL_IMPL = 0xfbF029508c061B440D0cF7Fd639e77Fb2E196241;

  // https://etherscan.io/address/0x4e1c7865e7BE78A7748724Fa0409e88dc14E67aA
  ILendingPoolConfigurator internal constant POOL_CONFIGURATOR =
    ILendingPoolConfigurator(0x4e1c7865e7BE78A7748724Fa0409e88dc14E67aA);

  // https://etherscan.io/address/0x8e5E28f273E3a6612A9C5d6F16aa67DA156042F4
  address internal constant POOL_CONFIGURATOR_IMPL = 0x8e5E28f273E3a6612A9C5d6F16aa67DA156042F4;

  // https://etherscan.io/address/0xB8a7bc0d13B1f5460513040a97F404b4fea7D2f3
  IAaveOracle internal constant ORACLE = IAaveOracle(0xB8a7bc0d13B1f5460513040a97F404b4fea7D2f3);

  // https://etherscan.io/address/0xfA3c34d734fe0106C87917683ca45dffBe3b3B00
  ILendingRateOracle internal constant LENDING_RATE_ORACLE =
    ILendingRateOracle(0xfA3c34d734fe0106C87917683ca45dffBe3b3B00);

  // https://etherscan.io/address/0x71B53fC437cCD988b1b89B1D4605c3c3d0C810ea
  IAaveProtocolDataProvider internal constant AAVE_PROTOCOL_DATA_PROVIDER =
    IAaveProtocolDataProvider(0x71B53fC437cCD988b1b89B1D4605c3c3d0C810ea);

  // https://etherscan.io/address/0x837696219C9a3775a856BEBC02DB1fA918C8a46e
  address internal constant LENDING_POOL_COLLATERAL_MANAGER =
    0x837696219C9a3775a856BEBC02DB1fA918C8a46e;

  // https://etherscan.io/address/0xAce1d11d836cb3F51Ef658FD4D353fFb3c301218
  address internal constant POOL_ADMIN = 0xAce1d11d836cb3F51Ef658FD4D353fFb3c301218;

  // https://etherscan.io/address/0x33B09130b035d6D7e57d76fEa0873d9545FA7557
  address internal constant EMERGENCY_ADMIN = 0x33B09130b035d6D7e57d76fEa0873d9545FA7557;

  // https://etherscan.io/address/0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c
  ICollector internal constant COLLECTOR = ICollector(0x464C71f6c2F760DdA6093dCB91C24c39e5d6e18c);

  // https://etherscan.io/address/0xF4a1F5fEA79C3609514A417425971FadC10eCfBE
  address internal constant PERMISSION_MANAGER = 0xF4a1F5fEA79C3609514A417425971FadC10eCfBE;
}
library AaveV2EthereumArcAssets {
  // https://etherscan.io/address/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
  address internal constant USDC_UNDERLYING = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;

  uint8 internal constant USDC_DECIMALS = 6;

  // https://etherscan.io/address/0xd35f648C3C7f17cd1Ba92e5eac991E3EfcD4566d
  address internal constant USDC_A_TOKEN = 0xd35f648C3C7f17cd1Ba92e5eac991E3EfcD4566d;

  // https://etherscan.io/address/0xe8D876034F96081063cD57Cd87b94a156b4E03E1
  address internal constant USDC_V_TOKEN = 0xe8D876034F96081063cD57Cd87b94a156b4E03E1;

  // https://etherscan.io/address/0x986b5E1e1755e3C2440e960477f25201B0a8bbD4
  address internal constant USDC_ORACLE = 0x986b5E1e1755e3C2440e960477f25201B0a8bbD4;

  // https://etherscan.io/address/0x81D7Bb11D682005B3Fca0Ef48381263BeC9b2d1C
  address internal constant USDC_INTEREST_RATE_STRATEGY =
    0x81D7Bb11D682005B3Fca0Ef48381263BeC9b2d1C;

  // https://etherscan.io/address/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599
  address internal constant WBTC_UNDERLYING = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;

  uint8 internal constant WBTC_DECIMALS = 8;

  // https://etherscan.io/address/0xe6d6E7dA65A2C18109Ff56B7CBBdc7B706Fc13F8
  address internal constant WBTC_A_TOKEN = 0xe6d6E7dA65A2C18109Ff56B7CBBdc7B706Fc13F8;

  // https://etherscan.io/address/0xc371FB4513c23Fc962fe23B12cFBD75E1D37ED91
  address internal constant WBTC_V_TOKEN = 0xc371FB4513c23Fc962fe23B12cFBD75E1D37ED91;

  // https://etherscan.io/address/0xdeb288F737066589598e9214E782fa5A8eD689e8
  address internal constant WBTC_ORACLE = 0xdeb288F737066589598e9214E782fa5A8eD689e8;

  // https://etherscan.io/address/0x1205ACe6831E5518E00A16f1820cD73ce198bEF6
  address internal constant WBTC_INTEREST_RATE_STRATEGY =
    0x1205ACe6831E5518E00A16f1820cD73ce198bEF6;

  // https://etherscan.io/address/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
  address internal constant WETH_UNDERLYING = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

  uint8 internal constant WETH_DECIMALS = 18;

  // https://etherscan.io/address/0x319190E3Bbc595602A9E63B2bCfB61c6634355b1
  address internal constant WETH_A_TOKEN = 0x319190E3Bbc595602A9E63B2bCfB61c6634355b1;

  // https://etherscan.io/address/0x932167279A4ed3b879bA7eDdC85Aa83551f3989D
  address internal constant WETH_V_TOKEN = 0x932167279A4ed3b879bA7eDdC85Aa83551f3989D;

  // https://etherscan.io/address/0xC2B0945C6D0A842eC2a1345f08c4ef2060452B6A
  address internal constant WETH_INTEREST_RATE_STRATEGY =
    0xC2B0945C6D0A842eC2a1345f08c4ef2060452B6A;

  // https://etherscan.io/address/0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9
  address internal constant AAVE_UNDERLYING = 0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9;

  uint8 internal constant AAVE_DECIMALS = 18;

  // https://etherscan.io/address/0x89eFaC495C65d43619c661df654ec64fc10C0A75
  address internal constant AAVE_A_TOKEN = 0x89eFaC495C65d43619c661df654ec64fc10C0A75;

  // https://etherscan.io/address/0x0ac4c7790BC96923b71BfCee44a6923fd085E0c8
  address internal constant AAVE_V_TOKEN = 0x0ac4c7790BC96923b71BfCee44a6923fd085E0c8;

  // https://etherscan.io/address/0x6Df09E975c830ECae5bd4eD9d90f3A95a4f88012
  address internal constant AAVE_ORACLE = 0x6Df09E975c830ECae5bd4eD9d90f3A95a4f88012;

  // https://etherscan.io/address/0x5E4b5f5eb05E244632e0eA584525F11Dd03f5B38
  address internal constant AAVE_INTEREST_RATE_STRATEGY =
    0x5E4b5f5eb05E244632e0eA584525F11Dd03f5B38;
}
