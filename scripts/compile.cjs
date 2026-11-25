const fs=require('fs'),path=require('path'),solc=require('solc');
const root=path.resolve(__dirname,'..');
const input={language:'Solidity',sources:{'ProductPassport.sol':{content:fs.readFileSync(path.join(root,'contracts/ProductPassport.sol'),'utf8')}},settings:{evmVersion:'paris',optimizer:{enabled:true,runs:200},outputSelection:{'*':{'*':['abi','evm.bytecode.object']}}}};
const output=JSON.parse(solc.compile(JSON.stringify(input)));
for(const e of output.errors||[])if(e.severity==='error'){process.stderr.write(e.formattedMessage);process.exit(1)}
const c=output.contracts['ProductPassport.sol'].ProductPassport;
fs.mkdirSync(path.join(root,'blockchain'),{recursive:true});
fs.writeFileSync(path.join(root,'blockchain/ProductPassport.json'),JSON.stringify({compiler:solc.version(),abi:c.abi,bytecode:'0x'+c.evm.bytecode.object},null,2));
console.log('Compiled ProductPassport');
