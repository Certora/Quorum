// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {AaveV3TreasuryProcedure} from '../../../contracts/procedures/AaveV3TreasuryProcedure.sol';
import {AaveV3OracleProcedure} from '../../../contracts/procedures/AaveV3OracleProcedure.sol';
import {AaveV3IncentiveProcedure} from '../../../contracts/procedures/AaveV3IncentiveProcedure.sol';
import {AaveV3DefaultRateStrategyProcedure} from '../../../contracts/procedures/AaveV3DefaultRateStrategyProcedure.sol';
import {IOwnable} from 'solidity-utils/contracts/transparent-proxy/interfaces/IOwnable.sol';
import '../../../interfaces/IMarketReportTypes.sol';
import {IRewardsController} from '../../../../contracts/rewards/interfaces/IRewardsController.sol';
import {IOwnable} from 'solidity-utils/contracts/transparent-proxy/interfaces/IOwnable.sol';
import {RevenueSplitter} from '../../../../contracts/treasury/RevenueSplitter.sol';

contract AaveV3PeripheryBatch is
  AaveV3TreasuryProcedure,
  AaveV3OracleProcedure,
  AaveV3IncentiveProcedure
{
  PeripheryReport internal _report;

  constructor(
    address poolAdmin,
    MarketConfig memory config,
    address poolAddressesProvider,
    address setupBatch
  ) {
    if (config.proxyAdmin == address(0)) {
      _report.proxyAdmin = address(new ProxyAdmin{salt: config.salt}());
      IOwnable(_report.proxyAdmin).transferOwnership(poolAdmin);
    } else {
      _report.proxyAdmin = config.proxyAdmin;
    }

    _report.aaveOracle = _deployAaveOracle(config.oracleDecimals, poolAddressesProvider);

    if (config.treasury == address(0)) {
      TreasuryReport memory treasuryReport = _deployAaveV3Treasury(
        poolAdmin,
        _report.proxyAdmin,
        config.salt
      );

      _report.treasury = treasuryReport.treasury;
      _report.treasuryImplementation = treasuryReport.treasuryImplementation;
    } else {
      _report.treasury = config.treasury;
    }

    if (
      config.treasuryPartner != address(0) &&
      config.treasurySplitPercent > 0 &&
      config.treasurySplitPercent < 100_00
    ) {
      _report.revenueSplitter = address(
        new RevenueSplitter(_report.treasury, config.treasuryPartner, config.treasurySplitPercent)
      );
    }

    if (config.incentivesProxy == address(0)) {
      (_report.emissionManager, _report.rewardsControllerImplementation) = _deployIncentives(
        setupBatch
      );
    } else {
      _report.emissionManager = IRewardsController(config.incentivesProxy).getEmissionManager();
    }
  }

  function getPeripheryReport() external view returns (PeripheryReport memory) {
    return _report;
  }
}
