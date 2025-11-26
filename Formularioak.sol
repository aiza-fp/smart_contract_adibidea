// SPDX-License-Identifier: MIT
// REMIX-EN KONPILATUA, SOLIDITY 0.8.19 BERTSIOAREKIN ETA 'EVM LONDON' JARRIZ
pragma solidity ^0.8.0;

contract Formularioak {
    // Define a struct with two strings: zenbakia and datuak
    struct Form {
        uint256 zenbakia;
        string datu1;
        string datu2;
    }

    address private owner;
    // Mapping to store forms using a uint256 identifier
    mapping(uint256 => Form) private forms;
    // Integer to count all zenbakia identifiers
    uint256 private formCount;

    event FormCreated(uint256 indexed zenbakia, string datu1, string datu2);
    event FormUpdated(uint256 indexed zenbakia, string datu1, string datu2);

    constructor() {
        owner = msg.sender; // Set the contract deployer as the owner
        formCount = 0;
    }

    // Modifier to restrict function access to the contract owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the contract owner can perform this action");
        _;
    }

    function createForm(string memory _datu1, string memory _datu2) public onlyOwner returns (uint256) {        
        formCount++;
        forms[formCount] = Form(formCount, _datu1, _datu2);        
        emit FormCreated(formCount, _datu1, _datu2);
        return formCount;
    }

    function updateForm(uint256 _zenbakia, string memory _datu1, string memory _datu2) public onlyOwner {
        // Check if the form exists by verifying that the zenbakia field matches the key
        require(forms[_zenbakia].zenbakia == _zenbakia && _zenbakia > 0, "Form does not exist");
        forms[_zenbakia] = Form(_zenbakia, _datu1, _datu2);
        emit FormUpdated(_zenbakia, _datu1, _datu2);
    }

    function getForm(uint256 _zenbakia) public view returns (string memory, string memory) {
        // Check if the form exists by verifying that the zenbakia field matches the key
        require(forms[_zenbakia].zenbakia == _zenbakia && _zenbakia > 0, "Form does not exist");
        Form memory form = forms[_zenbakia];
        return (form.datu1, form.datu2);
    }

    function getFormCount() public view returns (uint256) {
        return formCount;
    }
}
