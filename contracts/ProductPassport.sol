// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.30;

/// @notice Local-development product custody and append-only lifecycle history.
contract ProductPassport {
    enum Stage { Registered, Collected, Inspected, Repaired, Recycled }
    struct Product { string label; string deviceType; address owner; address pendingOwner; Stage stage; bool exists; }
    struct Record { uint256 timestamp; address actor; string action; string detail; bytes32 evidenceHash; }
    mapping(bytes32 => Product) private products;
    mapping(bytes32 => Record[]) private history;
    bytes32[] private ids;
    event Recorded(bytes32 indexed productId, address indexed actor, string action, bytes32 evidenceHash);
    modifier onlyOwner(bytes32 id) { require(products[id].exists, "Unknown product"); require(products[id].owner == msg.sender, "Current owner only"); _; }
    function register(bytes32 id, string calldata label, string calldata deviceType, bytes32 evidence) external {
        require(id != bytes32(0), "Empty ID"); require(!products[id].exists, "Already registered");
        require(bytes(label).length > 0 && bytes(label).length <= 120, "Label length");
        require(bytes(deviceType).length > 0 && bytes(deviceType).length <= 60, "Device type length");
        products[id] = Product(label, deviceType, msg.sender, address(0), Stage.Registered, true); ids.push(id);
        record(id, "Registered", "Product passport created", evidence);
    }
    function proposeTransfer(bytes32 id, address recipient) external onlyOwner(id) {
        require(products[id].stage != Stage.Recycled, "Product recycled");
        require(recipient != address(0) && recipient != msg.sender, "Invalid recipient");
        require(products[id].pendingOwner == address(0), "Transfer pending");
        products[id].pendingOwner=recipient; record(id, "Transfer proposed", addressString(recipient), bytes32(0));
    }
    function acceptTransfer(bytes32 id) external {
        Product storage p=products[id];require(p.exists, "Unknown product");
        require(p.pendingOwner == msg.sender, "Named recipient only");
        p.owner=msg.sender;p.pendingOwner=address(0);record(id, "Transfer accepted", "Custody accepted by recipient", bytes32(0));
    }
    function cancelTransfer(bytes32 id) external onlyOwner(id) {
        require(products[id].pendingOwner != address(0), "No pending transfer");
        products[id].pendingOwner=address(0);record(id, "Transfer cancelled", "Owner cancelled pending handoff", bytes32(0));
    }
    function updateStage(bytes32 id, Stage next, string calldata detail, bytes32 evidence) external onlyOwner(id) {
        Product storage p=products[id];require(p.stage != Stage.Recycled, "Product recycled");
        require(p.pendingOwner == address(0), "Resolve pending transfer first");
        require(bytes(detail).length > 0 && bytes(detail).length <= 500, "Detail length");
        bool valid=(p.stage==Stage.Registered && next==Stage.Collected)
            || (p.stage==Stage.Collected && next==Stage.Inspected)
            || (p.stage==Stage.Inspected && (next==Stage.Repaired || next==Stage.Recycled))
            || (p.stage==Stage.Repaired && (next==Stage.Collected || next==Stage.Inspected));
        require(valid, "Invalid lifecycle transition");p.stage=next;
        string[5] memory names=["Registered","Collected","Inspected","Repaired","Recycled"];
        record(id,names[uint(next)],detail,evidence);
    }
    function appendNote(bytes32 id,string calldata detail,bytes32 evidence) external onlyOwner(id) {
        require(bytes(detail).length > 0 && bytes(detail).length <= 500,"Detail length");
        record(id,"Note",detail,evidence);
    }
    function getProduct(bytes32 id) external view returns(Product memory) {require(products[id].exists,"Unknown product");return products[id];}
    function productCount() external view returns(uint) {return ids.length;}
    function productIdAt(uint index) external view returns(bytes32) {return ids[index];}
    function historyCount(bytes32 id) external view returns(uint) {return history[id].length;}
    function historyAt(bytes32 id,uint index) external view returns(Record memory) {return history[id][index];}
    function record(bytes32 id,string memory action,string memory detail,bytes32 evidence) private {
        history[id].push(Record(block.timestamp,msg.sender,action,detail,evidence));emit Recorded(id,msg.sender,action,evidence);
    }
    function addressString(address a) private pure returns(string memory) {
        bytes memory out=new bytes(42);out[0]='0';out[1]='x';bytes16 hexChars='0123456789abcdef';
        for(uint i=0;i<20;i++){uint8 b=uint8(uint160(a)>>(8*(19-i)));out[2+i*2]=hexChars[b>>4];out[3+i*2]=hexChars[b&15];}return string(out);
    }
}
