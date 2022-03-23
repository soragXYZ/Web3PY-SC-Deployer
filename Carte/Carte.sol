// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./openzeppelin-contracts/contracts/token/ERC721/ERC721.sol";
import "./openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "./openzeppelin-contracts/contracts/utils/Counters.sol";
import "./openzeppelin-contracts/contracts/access/Ownable.sol";
//1643

contract Card is ERC721URIStorage, Ownable {

    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct Doc {
        string docURI;
        bytes32 docHash;
        uint256 timestamp;
    }

    address[] internal _controllers;
    mapping(address => bool) internal _isController;


    /* *************************************** */
    // Mapping for documents.
    mapping(bytes32 => Doc) internal _documents;
    mapping(bytes32 => uint256) internal _indexOfDocHashes;
    bytes32[] internal _docHashes;
    /* ************************************** */

    /** @dev Modifier to verify if caller is controller.
    */
    modifier onlyController() {
        require(_isController[msg.sender], "Not a controller");
        _;
    }

    event DocumentRemoved(bytes32 indexed _name, string _uri, bytes32 _documentHash);
    event DocumentUpdated(bytes32 indexed _name, string _uri, bytes32 _documentHash);



    constructor (string memory tokenURI, uint256 parts, address minter) ERC721 ("Card", "CARD") {
        
        for(uint i=0; i < parts; i++){
            _tokenIds.increment();
            uint256 newItemId = _tokenIds.current();
            _mint(minter, newItemId);
            _setTokenURI(newItemId, tokenURI);
        }
    }

    function totalSupply() external view returns(uint256) {
        
        return _tokenIds.current();
    }

    function forceTransfer(
        address from,
        address to,
        uint256 tokenId,
        string calldata
    ) external onlyController {
        _transfer(from, to, tokenId);
    }

    function changeURI(string memory tokenURI) external onlyController {
        for( uint256 i=1; i <= _tokenIds.current(); i++)
            _setTokenURI(i, tokenURI);
    }


    /************************************ Token controllers *****************************************/
    /**
    * @dev Get the list of controllers as defined by the token contract.
    * @return List of addresses of all the controllers.
    */
    function controllers() external view returns (address[] memory) {
        return _controllers;
    }

    /**
    * @dev Set list of token controllers.
    * @param operators Controller addresses.
    */
    function _setControllers(address[] memory operators) internal {
        for (uint i = 0; i<_controllers.length; i++){
        _isController[_controllers[i]] = false;
        }
        for (uint j = 0; j<operators.length; j++){
        _isController[operators[j]] = true;
        }
        _controllers = operators;
    }

    /**
    * @dev Set list of token controllers.
    * @param operators Controller addresses.
    */
    function setControllers(address[] calldata operators) external onlyOwner {
        _setControllers(operators);
    }

    /**
    * @dev Access a document associated with the token.
    * @param name Short name (represented as a bytes32) associated to the document.
    * @return Requested document + document hash + document timestamp.
    */
    function getDocument(bytes32 name) external view returns (string memory, bytes32, uint256) {
        require(bytes(_documents[name].docURI).length != 0); // Action Blocked - Empty document
        return (
        _documents[name].docURI,
        _documents[name].docHash,
        _documents[name].timestamp
        );
    }
    /**
    * @dev Associate a document with the token.
    * @param name Short name (represented as a bytes32) associated to the document.
    * @param uri Document content.
    * @param documentHash Hash of the document [optional parameter].
    */
    function setDocument(bytes32 name, string calldata uri, bytes32 documentHash) external onlyController {
        _documents[name] = Doc({
        docURI: uri,
        docHash: documentHash,
        timestamp: block.timestamp
        });

        if (_indexOfDocHashes[documentHash] == 0) {
        _docHashes.push(documentHash);
        _indexOfDocHashes[documentHash] = _docHashes.length;
        }

        emit DocumentUpdated(name, uri, documentHash);
    }

    function removeDocument(bytes32 _name) external onlyController {
        require(bytes(_documents[_name].docURI).length != 0, "Document doesnt exist"); // Action Blocked - Empty document

        Doc memory data = _documents[_name];

        uint256 index1 = _indexOfDocHashes[data.docHash];
        require(index1 > 0, "Invalid index"); //Indexing starts at 1, 0 is not allowed

        // move the last item into the index being vacated
        bytes32 lastValue = _docHashes[_docHashes.length - 1];
        _docHashes[index1 - 1] = lastValue; // adjust for 1-based indexing
        _indexOfDocHashes[lastValue] = index1;

        //_totalPartitions.length -= 1;
        _docHashes.pop();
        _indexOfDocHashes[data.docHash] = 0;

        delete _documents[_name];

        emit DocumentRemoved(_name, data.docURI, data.docHash);
    }

    function getAllDocuments() external view returns (bytes32[] memory) {
        return _docHashes;
    }


}