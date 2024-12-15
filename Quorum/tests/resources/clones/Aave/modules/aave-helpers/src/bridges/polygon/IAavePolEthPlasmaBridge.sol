// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

/// @title IAavePolEthPlasmaBridge
/// @author efecarranza.eth
/// @notice Interface for AavePolEthPlasmaBridge
interface IAavePolEthPlasmaBridge {
  /// @dev The called method is not available on this chain
  error InvalidChain();

  /// @dev Emitted when a bridge is initiated
  event Bridge(address token, uint256 amount);

  /// @dev Emitted when the bridge transaction is confirmed
  event ConfirmExit(bytes proof);

  /// @dev Emitted when a token bridge is finalized
  event Exit(address indexed token);

  /// @dev Emitted when multiple token bridges are finalized
  event ExitBatch(address[] indexed tokens);

  /// @dev Emitted when token is withdrawn to the Aave Collector
  event WithdrawToCollector(address token, uint256 amount);

  /// @dev The mainnet address of the Predicate contract to confirm withdrawal
  function ERC20_PREDICATE_BURN() external view returns (address);

  /// @dev The mainnet address of the withdrawal contract to exit the bridge
  function WITHDRAW_MANAGER() external view returns (address);

  /// @dev The mainnet address of the MATIC token
  function MATIC_MAINNET() external view returns (address);

  /// @dev The polygon address of the MATIC token
  function MATIC_POLYGON() external view returns (address);

  /// This function withdraws MATIC from Polygon to Mainnet. exit() needs
  /// to be called on mainnet with the corresponding burnProof in order to complete.
  /// @notice Polygon only. Function will revert if called from other network.
  /// @param amount Amount of tokens to withdraw
  function bridge(uint256 amount) external;

  /// This function confirms the withdrawal process from Polygon to Mainnet (Step 2 of 3)
  /// Burn proof is generated via API. Please see README.md
  /// @notice Mainnet only. Function will revert if called from other network.
  /// @param burnProof Burn proof generated via API.
  function confirmExit(bytes calldata burnProof) external;

  /// This function completes the withdrawal process from Polygon to Mainnet.
  /// @notice Mainnet only. Function will revert if called from other network.
  function exit() external;

  /// Withdraws MATIC on Mainnet contract to Aave V3 Collector.
  /// @notice Mainnet only. Function will revert if called from other network.
  function withdrawToCollector() external;
}
