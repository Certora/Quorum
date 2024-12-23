// AUTOGENERATED - MANUALLY CHANGES WILL BE REVERTED BY THE GENERATOR
// SPDX-License-Identifier: MIT
pragma solidity >=0.6.0;

import {IPoolAddressesProvider, IPool, IPoolConfigurator, IAaveOracle, IPoolDataProvider, IACLManager} from './AaveV3.sol';
import {ICollector} from './common/ICollector.sol';
library AaveV3BaseSepolia {
  // https://sepolia.basescan.org/address/0x150E9a8b83b731B9218a5633F1E804BC82508A46
  IPoolAddressesProvider internal constant POOL_ADDRESSES_PROVIDER =
    IPoolAddressesProvider(0x150E9a8b83b731B9218a5633F1E804BC82508A46);

  // https://sepolia.basescan.org/address/0xbE781D7Bdf469f3d94a62Cdcc407aCe106AEcA74
  IPool internal constant POOL = IPool(0xbE781D7Bdf469f3d94a62Cdcc407aCe106AEcA74);

  // https://sepolia.basescan.org/address/0x4200a89Bd036745918889D6dCC5685A4C6F01C24
  IPoolConfigurator internal constant POOL_CONFIGURATOR =
    IPoolConfigurator(0x4200a89Bd036745918889D6dCC5685A4C6F01C24);

  // https://sepolia.basescan.org/address/0x9Ba30437Ba63AA2902319DE1B3f0E25a18826842
  IAaveOracle internal constant ORACLE = IAaveOracle(0x9Ba30437Ba63AA2902319DE1B3f0E25a18826842);

  // https://sepolia.basescan.org/address/0x6ec33534BE07d45cc4E02Fbd127F8ed2aE919a6b
  address internal constant ACL_ADMIN = 0x6ec33534BE07d45cc4E02Fbd127F8ed2aE919a6b;

  // https://sepolia.basescan.org/address/0xb880879303D35a82B1888a4A6d47D2ef0653E4A2
  IACLManager internal constant ACL_MANAGER =
    IACLManager(0xb880879303D35a82B1888a4A6d47D2ef0653E4A2);

  // https://sepolia.basescan.org/address/0xAF4646B0131af8fc0DC435AF7F7d303Ac131E072
  IPoolDataProvider internal constant AAVE_PROTOCOL_DATA_PROVIDER =
    IPoolDataProvider(0xAF4646B0131af8fc0DC435AF7F7d303Ac131E072);

  // https://sepolia.basescan.org/address/0x07D04EfAAA0Ac69D19d107795aF247C42Eb50F1C
  address internal constant POOL_IMPL = 0x07D04EfAAA0Ac69D19d107795aF247C42Eb50F1C;

  // https://sepolia.basescan.org/address/0x9E7DF170E44093d6738057157CA048794B02555d
  address internal constant POOL_CONFIGURATOR_IMPL = 0x9E7DF170E44093d6738057157CA048794B02555d;

  // https://sepolia.basescan.org/address/0x294FF52d234a7e09E9642F846702A45337ceB2E2
  address internal constant DEFAULT_INCENTIVES_CONTROLLER =
    0x294FF52d234a7e09E9642F846702A45337ceB2E2;

  // https://sepolia.basescan.org/address/0x1F95c29C9E686e4f438ED5D13cF0B7430B9F39ec
  address internal constant EMISSION_MANAGER = 0x1F95c29C9E686e4f438ED5D13cF0B7430B9F39ec;

  // https://sepolia.basescan.org/address/0x67F521ca716dD9413fd2D2AfdEbEE9285289d2cB
  ICollector internal constant COLLECTOR = ICollector(0x67F521ca716dD9413fd2D2AfdEbEE9285289d2cB);

  // https://sepolia.basescan.org/address/0xA9E3fFb25C369e44862DD3e87Be4420abb879965
  address internal constant DEFAULT_A_TOKEN_IMPL_REV_1 = 0xA9E3fFb25C369e44862DD3e87Be4420abb879965;

  // https://sepolia.basescan.org/address/0x95eeA7A0b16C8ee3A923D3F5ebe6d77C0332084c
  address internal constant DEFAULT_VARIABLE_DEBT_TOKEN_IMPL_REV_1 =
    0x95eeA7A0b16C8ee3A923D3F5ebe6d77C0332084c;

  // https://sepolia.basescan.org/address/0xAE252DA024783d1813C890d82642bbED120c3093
  address internal constant STATA_FACTORY = 0xAE252DA024783d1813C890d82642bbED120c3093;

  // https://sepolia.basescan.org/address/0x3d2ee1AB8C3a597cDf80273C684dE0036481bE3a
  address internal constant CONFIG_ENGINE = 0x3d2ee1AB8C3a597cDf80273C684dE0036481bE3a;

  // https://sepolia.basescan.org/address/0x0ffE481FBF0AE2282A5E1f701fab266aF487A97D
  address internal constant L2_ENCODER = 0x0ffE481FBF0AE2282A5E1f701fab266aF487A97D;

  // https://sepolia.basescan.org/address/0x5A6c2685b9dd22705203C99d7Fc30AE53C4c7513
  address internal constant POOL_ADDRESSES_PROVIDER_REGISTRY =
    0x5A6c2685b9dd22705203C99d7Fc30AE53C4c7513;

  // https://sepolia.basescan.org/address/0xb0633e01310a09C1Ee71a96c057DcF9c13fd6F62
  address internal constant UI_INCENTIVE_DATA_PROVIDER = 0xb0633e01310a09C1Ee71a96c057DcF9c13fd6F62;

  // https://sepolia.basescan.org/address/0xdc5D225Df17df184d11015B91C4A10cd7834e2aC
  address internal constant WALLET_BALANCE_PROVIDER = 0xdc5D225Df17df184d11015B91C4A10cd7834e2aC;

  // https://sepolia.basescan.org/address/0xd5DDE725b0A2dE43fBDb4E488A7fdA389210d461
  address internal constant WETH_GATEWAY = 0xd5DDE725b0A2dE43fBDb4E488A7fdA389210d461;
}
library AaveV3BaseSepoliaAssets {
  // https://sepolia.basescan.org/address/0x036CbD53842c5426634e7929541eC2318f3dCF7e
  address internal constant USDC_UNDERLYING = 0x036CbD53842c5426634e7929541eC2318f3dCF7e;

  uint8 internal constant USDC_DECIMALS = 6;

  // https://sepolia.basescan.org/address/0xfE45Bf4dEF7223Ab1Bf83cA17a4462Ef1647F7FF
  address internal constant USDC_A_TOKEN = 0xfE45Bf4dEF7223Ab1Bf83cA17a4462Ef1647F7FF;

  // https://sepolia.basescan.org/address/0x5E531B00C86C2D0014020183DaFE7c17C4aA90D8
  address internal constant USDC_V_TOKEN = 0x5E531B00C86C2D0014020183DaFE7c17C4aA90D8;

  // https://sepolia.basescan.org/address/0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165
  address internal constant USDC_ORACLE = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;

  // https://sepolia.basescan.org/address/0xff1DB744F1275f8e04A62A7E5D663575F3a774B6
  address internal constant USDC_INTEREST_RATE_STRATEGY =
    0xff1DB744F1275f8e04A62A7E5D663575F3a774B6;

  // https://sepolia.basescan.org/address/0x808456652fdb597867f38412077A9182bf77359F
  address internal constant EURC_UNDERLYING = 0x808456652fdb597867f38412077A9182bf77359F;

  uint8 internal constant EURC_DECIMALS = 6;

  // https://sepolia.basescan.org/address/0x70B607b3cdED31635779781d42540580D4Ac18F4
  address internal constant EURC_A_TOKEN = 0x70B607b3cdED31635779781d42540580D4Ac18F4;

  // https://sepolia.basescan.org/address/0xEa1b67213437E753656B209d1d3d16c1DFE424fd
  address internal constant EURC_V_TOKEN = 0xEa1b67213437E753656B209d1d3d16c1DFE424fd;

  // https://sepolia.basescan.org/address/0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165
  address internal constant EURC_ORACLE = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;

  // https://sepolia.basescan.org/address/0xff1DB744F1275f8e04A62A7E5D663575F3a774B6
  address internal constant EURC_INTEREST_RATE_STRATEGY =
    0xff1DB744F1275f8e04A62A7E5D663575F3a774B6;

  // https://sepolia.basescan.org/address/0x4200000000000000000000000000000000000006
  address internal constant WETH_UNDERLYING = 0x4200000000000000000000000000000000000006;

  uint8 internal constant WETH_DECIMALS = 18;

  // https://sepolia.basescan.org/address/0x6dE9f4b8d4A52D15F1372ef463e27AeAa8a3FdF4
  address internal constant WETH_A_TOKEN = 0x6dE9f4b8d4A52D15F1372ef463e27AeAa8a3FdF4;

  // https://sepolia.basescan.org/address/0x80bEA6A08B3c2df41B48F27c983C3238f1144093
  address internal constant WETH_V_TOKEN = 0x80bEA6A08B3c2df41B48F27c983C3238f1144093;

  // https://sepolia.basescan.org/address/0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1
  address internal constant WETH_ORACLE = 0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1;

  // https://sepolia.basescan.org/address/0xff1DB744F1275f8e04A62A7E5D663575F3a774B6
  address internal constant WETH_INTEREST_RATE_STRATEGY =
    0xff1DB744F1275f8e04A62A7E5D663575F3a774B6;

  // https://sepolia.basescan.org/address/0x3e138010792d63e4af70dD7F2401C9cdE0eaf3C8
  address internal constant USDX_UNDERLYING = 0x3e138010792d63e4af70dD7F2401C9cdE0eaf3C8;

  uint8 internal constant USDX_DECIMALS = 18;

  // https://sepolia.basescan.org/address/0x7E60de07156fdA16A74F3700725e2bbB5CFC8CB8
  address internal constant USDX_A_TOKEN = 0x7E60de07156fdA16A74F3700725e2bbB5CFC8CB8;

  // https://sepolia.basescan.org/address/0xed47C3087a7B41a4F2cA93747DDDc368f8EcDE47
  address internal constant USDX_V_TOKEN = 0xed47C3087a7B41a4F2cA93747DDDc368f8EcDE47;

  // https://sepolia.basescan.org/address/0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165
  address internal constant USDX_ORACLE = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;

  // https://sepolia.basescan.org/address/0xff1DB744F1275f8e04A62A7E5D663575F3a774B6
  address internal constant USDX_INTEREST_RATE_STRATEGY =
    0xff1DB744F1275f8e04A62A7E5D663575F3a774B6;

  // https://sepolia.basescan.org/address/0xb17966889E3D914CCf9A11bA0Fd71870B03727AF
  address internal constant USDX_STATA_TOKEN = 0xb17966889E3D914CCf9A11bA0Fd71870B03727AF;
}
library AaveV3BaseSepoliaEModes {
  uint8 internal constant NONE = 0;
}
library AaveV3BaseSepoliaExternalLibraries {
  // https://sepolia.basescan.org/address/0xb32381feFFF45eE9F47fD2f2cF83C832637d6EF0
  address internal constant FLASHLOAN_LOGIC = 0xb32381feFFF45eE9F47fD2f2cF83C832637d6EF0;

  // https://sepolia.basescan.org/address/0x4c52FE2162200bf26c314d7bbd8611699139d553
  address internal constant BORROW_LOGIC = 0x4c52FE2162200bf26c314d7bbd8611699139d553;

  // https://sepolia.basescan.org/address/0x97dCbFaE5372A63128F141E8C0BC2c871Ca5F604
  address internal constant BRIDGE_LOGIC = 0x97dCbFaE5372A63128F141E8C0BC2c871Ca5F604;

  // https://sepolia.basescan.org/address/0x88F864670De467aA73CD45325F9652C578C8AB85
  address internal constant E_MODE_LOGIC = 0x88F864670De467aA73CD45325F9652C578C8AB85;

  // https://sepolia.basescan.org/address/0x80d16970B31243Fe67DaB028115f3E4c3E3510Ad
  address internal constant LIQUIDATION_LOGIC = 0x80d16970B31243Fe67DaB028115f3E4c3E3510Ad;

  // https://sepolia.basescan.org/address/0xA58FB47bE9074828215A173564C0CD10f6F249bf
  address internal constant POOL_LOGIC = 0xA58FB47bE9074828215A173564C0CD10f6F249bf;

  // https://sepolia.basescan.org/address/0x2b22E425C1322fbA0DbF17bb1dA25d71811EE7ba
  address internal constant SUPPLY_LOGIC = 0x2b22E425C1322fbA0DbF17bb1dA25d71811EE7ba;
}