/**
 * SPDX-License-Identifier: MIT
 *
 * Copyright (c) 2018-2020 CENTRE SECZ
 */

pragma solidity 0.6.12;

contract FiatTokenV2 {
    mapping(address => uint256) internal balances;
    mapping(address => bool) internal blacklisted;
    uint256 internal _initializedVersion;
    
    function _transfer(address from, address to, uint256 value) internal {
    }
    
    function version() external pure virtual returns (string memory) {
        return "2";
    }
}
