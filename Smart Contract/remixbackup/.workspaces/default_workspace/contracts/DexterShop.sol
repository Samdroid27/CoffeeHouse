pragma solidity >=0.8.0;

// Creating a Smart contract for customers instance

contract Customer{
    
    uint256 public tokenPrice=1000;
    address owner;
    
    // Customers wallet consisting money and tokens
    struct Wallet{
        uint256 money;
        uint256 token;
    }
    
    //Mapping wallets to address
    mapping (address => Wallet) wallets;
    
    //address array of connected wallets
    address[] public Accounts;
    
     // Creating a Wallet for the deployed contract address
    constructor(){
        owner = msg.sender;
        Wallet storage wallet = wallets[owner];
        wallet.money = 0;
        wallet.token = 0;
        Accounts.push(owner);
    }
    
    //Getting all the connected wallets
    function getWallets() view public returns(address[] memory) {
       return Accounts;
    }
    
    //Adding wallets created to connected wallet array
    function setWallet(address _address) public{
        Accounts.push(_address);
    }
    
    // Getting address of the current contract instance
    function getAddress() view public returns(address){
        return owner;
    }

    //Getting token count of the current wallet
    function getTokenCount() view public returns(uint256){
        return wallets[owner].token;
    }
    
    //Getting balance of the current wallet
    function getBalance() view public returns(uint256){
        return wallets[owner].money;
    }
    
    //Getting token price
    function getTokenPrice() view public returns(uint256){
        return tokenPrice;
    }
    
    //Depositing money in wallet
    function deposit(uint256 amt) public{
        wallets[owner].money += amt;
    }
    
    //Purchasing token for the owner of the wallet
    function purchaseToken(uint256 val) public{
        
        //Owner should have sufficient money to buy the tokens
        require((val*tokenPrice)<=wallets[owner].money,"Not enough balance");
        
        //Updating owner's wallet
        wallets[owner].money = wallets[owner].money-(val*tokenPrice);
        wallets[owner].token +=val;
    }
    
    //Spending token to enter the shop
    function spendtoken(uint256 val) public{
        
        //No. of tokens should to be spent should be atleast equal to the tokens held by the owner
        if(val<=wallets[owner].token){
            wallets[owner].token -= val;
        }
    }
    
    //Selling token 
    function sellToken(uint256 val,address buyer) public{
        // val is no. of token to be bought
        // buyer is the address of the buyer
        
        // no. of token should be less than or equal to tokens held by the owner
        require(val<=wallets[owner].token,"Not enough token");
        
        // buyers wallet should have enough money to buy the required no. of tokens
        require(val*tokenPrice<=wallets[buyer].money,"Not enough balance");
        
        //Updating owner's wallet
        wallets[owner].token -= val;
        wallets[owner].money += val*tokenPrice;
        
        //Updating buyer's wallet
        wallets[buyer].token += val;
        wallets[buyer].money -= val*tokenPrice;
    }
    
}