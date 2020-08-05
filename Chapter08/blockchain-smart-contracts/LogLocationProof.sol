// SPDX-License-Identifier: MIT
pragma solidity >=0.4.16 <0.7.0;

contract LogLocationProof {
    modifier onlyBy(address _account) {
        require(
            msg.sender == _account,
            "Sender not authorized to update this mapping!"
        );

        _; // The "_;"! will be replaced by the actual function body when the modifier is used.
    }

    // DeviceID_LatestLocationHistoryCID is a mapping which persists the latest CIDs for each sensor identified by its own ID
    mapping(address => string) private deviceIDToLatestCID;
    mapping(address => uint256) private deviceIDExists;

    // deviceIDs is an updated list of all the wallets associated with each device IDs
    address[] private deviceIDs;

    // MappingUpdated is emitted when the mapping is udpated with a new ID by sensors
    event MappingUpdated(address deviceID, string latestCID);

    // SetLatestCID is a setter function to udpate the mapping with the latest CID
    function setLatestCID(address deviceID, string memory latestCID)
        public
        onlyBy(deviceID)
    {
        deviceIDToLatestCID[deviceID] = latestCID;
        if (deviceIDExists[deviceID] == 0) {
            deviceIDs.push(deviceID);
            deviceIDExists[deviceID] = 1;
        }
        emit MappingUpdated(deviceID, latestCID);
    }

    // GetLatestCID returns the latest CID of a given sensor
    function getLatestCID(address deviceID)
        public
        view
        returns (string memory latestCID)
    {
        return deviceIDToLatestCID[deviceID];
    }

    // getIDByIndex function returns the address of the deviceIDs registry by the index
    function getIDByIndex(uint256 index) public view returns (address) {
        return deviceIDs[index];
    }

    // getDeviceIDsLength returns the length of the deviceIDs
    function getDeviceIDsLength() public view returns (uint256) {
        return deviceIDs.length;
    }
}
