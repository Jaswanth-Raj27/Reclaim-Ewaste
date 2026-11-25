const ganache=require('ganache'),path=require('path'),fs=require('fs');
const root=path.resolve(__dirname,'..');fs.mkdirSync(path.join(root,'.local/chain'),{recursive:true});
const server=ganache.server({chain:{chainId:1337,hardfork:'shanghai'},wallet:{totalAccounts:6,defaultBalance:1000},database:{dbPath:path.join(root,'.local/chain')},logging:{quiet:true}});
server.listen(8545,'127.0.0.1').then(()=>console.log('Reclaim local Ethereum node: http://127.0.0.1:8545 | chain 1337 | unlocked demo accounts, local use only')).catch(e=>{console.error(e.message);process.exit(1)});
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,async()=>{await server.close();process.exit(0)});
