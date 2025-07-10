/**
 * SPDX-License-Identifier: MIT
 *
 * Copyright (c) 2018 zOS Global Limited.
 */

pragma solidity 0.6.12;

contract UpgradeabilityProxy {
    bytes32 internal constant IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;
    
    constructor(address _logic, bytes memory _data) public payable {
        _setImplementation(_logic);
        if(_data.length > 0) {
            (bool success,) = _logic.delegatecall(_data);
            require(success);
        }
    }
    
    function _implementation() internal view returns (address) {
        return StorageSlot.getAddressSlot(IMPLEMENTATION_SLOT).value;
    }
    
    function _setImplementation(address newImplementation) internal {
        StorageSlot.getAddressSlot(IMPLEMENTATION_SLOT).value = newImplementation;
    }
    
    function _upgradeTo(address newImplementation) internal {
        _setImplementation(newImplementation);
    }
    
    function _fallback() internal {
        _delegate(_implementation());
    }
    
    function _delegate(address implementation) internal {
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), implementation, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
    
    function _beforeFallback() internal virtual {
    }
    
    fallback() external payable {
        _beforeFallback();
        _fallback();
    }
    
    receive() external payable {
        _beforeFallback();
        _fallback();
    }
}

library StorageSlot {
    struct AddressSlot {
        address value;
    }
    
    function getAddressSlot(bytes32 slot) internal pure returns (AddressSlot storage r) {
        assembly {
            r.slot := slot
        }
    }
}
