// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {IProposalGenericExecutor} from 'aave-helpers/src/interfaces/IProposalGenericExecutor.sol';
import {IRiskSteward} from './interfaces/IRiskSteward.sol';
import {AaveV3Arbitrum, AaveV3ArbitrumAssets} from 'aave-address-book/AaveV3Arbitrum.sol';

/**
 * @title Risk Steward Phase 2
 * @author BGD Labs (@bgdlabs)
 * - Snapshot: https://snapshot.org/#/aave.eth/proposal/0x4809f179e517e5745ec13eba8f40d98dab73ca65f8a141bd2f18cc16dcd0cc16
 * - Discussion: https://governance.aave.com/t/arfc-bgd-risk-steward-phase-2-risksteward/16204
 */
contract AaveV3Arbitrum_RiskStewardPhase2_20240805 is IProposalGenericExecutor {
  function execute() external {
    AaveV3Arbitrum.ACL_MANAGER.addRiskAdmin(AaveV3Arbitrum.RISK_STEWARD);
    IRiskSteward(AaveV3Arbitrum.RISK_STEWARD).setAddressRestricted(
      AaveV3ArbitrumAssets.GHO_UNDERLYING,
      true
    );
  }
}