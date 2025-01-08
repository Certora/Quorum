// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import '../../interfaces/IMarketReportTypes.sol';
import {IOwnable} from 'solidity-utils/contracts/transparent-proxy/interfaces/IOwnable.sol';
import {ACLManager} from '../../../contracts/protocol/configuration/ACLManager.sol';
import {IPoolConfigurator} from '../../../contracts/interfaces/IPoolConfigurator.sol';
import {IPoolAddressesProvider} from '../../../contracts/interfaces/IPoolAddressesProvider.sol';
import {PoolAddressesProvider} from '../../../contracts/protocol/configuration/PoolAddressesProvider.sol';
import {PoolAddressesProviderRegistry} from '../../../contracts/protocol/configuration/PoolAddressesProviderRegistry.sol';
import {IEmissionManager} from '../../../contracts/rewards/interfaces/IEmissionManager.sol';
import {IRewardsController} from '../../../contracts/rewards/interfaces/IRewardsController.sol';

contract AaveV3SetupProcedure {
  struct AddressProviderInput {
    InitialReport initialReport;
    address poolImplementation;
    address poolConfiguratorImplementation;
    address protocolDataProvider;
    address poolAdmin;
    address aaveOracle;
    address rewardsControllerProxy;
    address rewardsControllerImplementation;
    address priceOracleSentinel;
  }

  function _initialDeployment(
    address providerRegistry,
    address marketOwner,
    string memory marketId,
    uint256 providerId
  ) internal returns (InitialReport memory) {
    InitialReport memory report;

    report.poolAddressesProvider = address(new PoolAddressesProvider(marketId, address(this)));
    report.poolAddressesProviderRegistry = _deployPoolAddressesProviderRegistry(
      marketOwner,
      providerRegistry,
      report.poolAddressesProvider,
      providerId
    );
    return report;
  }

  function _setupAaveV3Market(
    Roles memory roles,
    MarketConfig memory config,
    InitialReport memory initialReport,
    address poolImplementation,
    address poolConfiguratorImplementation,
    address protocolDataProvider,
    address aaveOracle,
    address rewardsControllerImplementation,
    address priceOracleSentinel
  ) internal returns (SetupReport memory) {
    _validateMarketSetup(roles);

    SetupReport memory report = _setupPoolAddressesProvider(
      AddressProviderInput(
        initialReport,
        poolImplementation,
        poolConfiguratorImplementation,
        protocolDataProvider,
        roles.poolAdmin,
        aaveOracle,
        config.incentivesProxy,
        rewardsControllerImplementation,
        priceOracleSentinel
      )
    );

    report.aclManager = _setupACL(
      roles,
      initialReport.poolAddressesProvider,
      report.poolConfiguratorProxy,
      config.flashLoanPremiumTotal,
      config.flashLoanPremiumToProtocol
    );

    _transferMarketOwnership(roles, initialReport);

    return report;
  }

  function _deployPoolAddressesProviderRegistry(
    address marketOwner,
    address providerRegistry,
    address poolAddressesProvider,
    uint256 providerId
  ) internal returns (address) {
    address poolAddressesProviderRegistry;

    if (providerRegistry == address(0)) {
      poolAddressesProviderRegistry = address(new PoolAddressesProviderRegistry(address(this)));
      PoolAddressesProviderRegistry(poolAddressesProviderRegistry).registerAddressesProvider(
        poolAddressesProvider,
        providerId
      );
      IOwnable(poolAddressesProviderRegistry).transferOwnership(marketOwner);
    } else {
      poolAddressesProviderRegistry = providerRegistry;
    }

    return poolAddressesProviderRegistry;
  }

  function _setupPoolAddressesProvider(
    AddressProviderInput memory input
  ) internal returns (SetupReport memory) {
    SetupReport memory report;

    IPoolAddressesProvider provider = IPoolAddressesProvider(
      input.initialReport.poolAddressesProvider
    );
    provider.setPriceOracle(input.aaveOracle);
    provider.setPoolImpl(input.poolImplementation);
    provider.setPoolConfiguratorImpl(input.poolConfiguratorImplementation);
    provider.setPoolDataProvider(input.protocolDataProvider);

    report.poolProxy = address(provider.getPool());
    report.poolConfiguratorProxy = address(provider.getPoolConfigurator());

    if (input.priceOracleSentinel != address(0)) {
      provider.setPriceOracleSentinel(input.priceOracleSentinel);
    }

    bytes32 controllerId = keccak256('INCENTIVES_CONTROLLER');
    if (input.rewardsControllerProxy == address(0)) {
      require(
        input.rewardsControllerImplementation != address(0),
        'rewardsControllerImplementation must be set'
      );
      provider.setAddressAsProxy(controllerId, input.rewardsControllerImplementation);
      report.rewardsControllerProxy = provider.getAddress(controllerId);
      IEmissionManager emissionManager = IEmissionManager(
        IRewardsController(report.rewardsControllerProxy).EMISSION_MANAGER()
      );
      emissionManager.setRewardsController(report.rewardsControllerProxy);
      IOwnable(address(emissionManager)).transferOwnership(input.poolAdmin);
    } else {
      provider.setAddress(controllerId, input.rewardsControllerProxy);
      report.rewardsControllerProxy = provider.getAddress(controllerId);
    }
    return report;
  }

  function _setupACL(
    Roles memory roles,
    address poolAddressesProvider,
    address poolConfiguratorProxy,
    uint128 flashLoanPremiumTotal,
    uint128 flashLoanPremiumToProtocol
  ) internal returns (address) {
    IPoolAddressesProvider provider = IPoolAddressesProvider(poolAddressesProvider);

    // Temporal admin set to the contract
    provider.setACLAdmin(address(this));

    ACLManager manager = new ACLManager(IPoolAddressesProvider(poolAddressesProvider));
    address aclManager = address(manager);

    // Setup roles
    provider.setACLAdmin(roles.poolAdmin);

    provider.setACLManager(address(manager));

    _configureFlashloanParams(
      manager,
      poolConfiguratorProxy,
      flashLoanPremiumTotal,
      flashLoanPremiumToProtocol
    );

    manager.addPoolAdmin(roles.poolAdmin);

    manager.addEmergencyAdmin(roles.emergencyAdmin);

    manager.grantRole(manager.DEFAULT_ADMIN_ROLE(), roles.poolAdmin);

    manager.revokeRole(manager.DEFAULT_ADMIN_ROLE(), address(this));

    return aclManager;
  }

  function _configureFlashloanParams(
    ACLManager manager,
    address poolConfiguratorProxy,
    uint128 flashLoanPremiumTotal,
    uint128 flashLoanPremiumToProtocol
  ) internal {
    IPoolConfigurator configurator = IPoolConfigurator(poolConfiguratorProxy);
    manager.addPoolAdmin(address(this));

    configurator.updateFlashloanPremiumTotal(flashLoanPremiumTotal);
    configurator.updateFlashloanPremiumToProtocol(flashLoanPremiumToProtocol);

    manager.revokeRole(manager.POOL_ADMIN_ROLE(), address(this));
  }

  function _transferMarketOwnership(Roles memory roles, InitialReport memory report) internal {
    address addressesProviderOwner = IOwnable(report.poolAddressesProvider).owner();
    address marketOwner = IOwnable(report.poolAddressesProviderRegistry).owner();

    if (addressesProviderOwner == address(this)) {
      IOwnable(report.poolAddressesProvider).transferOwnership(roles.marketOwner);
    }

    if (marketOwner == address(this)) {
      IOwnable(report.poolAddressesProviderRegistry).transferOwnership(roles.marketOwner);
    }
  }

  function _validateMarketSetup(Roles memory roles) internal pure {
    require(roles.marketOwner != address(0), 'roles.marketOwner must be set');
  }
}