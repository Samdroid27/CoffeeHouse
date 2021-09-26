# Blockchain Project - Dexter’s Coffee Shop

## Requirements to be installed:
* Flask==0.12.2: pip install Flask==0.12.2
* Postman HTTP Client: https://www.getpostman.com/
* requests==2.18.4: pip install requests==2.18.4
* Programming Language Used: Python (Version: 3.9)

------------------------------
## Working of the Blockchain

For demonstration purposes, we have created 3 nodes at ports 5000, 5001, 5002 to
create a decentralized blockchain and used Postman for API calls and presenting
the corresponding response.

**A Block contains:**
>* Block Index
>* Previous Hash
>* Nonce
>* Timestamp
>* Transactions

**The difficulty level to mine a block :**
>A valid hash using SHA256 should have four leading zeros.

**During verification, two constraints are checked for the validity of blockchain:**
>1. The previous hash matches the hash of the previous block
>1. Hash of the current block has 4 leading zeros

**API calls available**

Route | Request Type | Description|
-------|------------|-------------|
| /get_chain  | GET|To get complete chain details|
| /update_chain  | GET|To update local copy of chain with the latest copy of blockchain|
| /is_valid  | GET|To check if the current copy of chain is valid or not.|
| /mine_block  | GET|To mine the block in the blockchain network|.
| /make_connections | POST|To establish connection between the nodes in the network.|
| /add_transaction  | POST|To add a new transaction in transaction pool that are ready to be mined.|
| /get_block  | POST|To get a particular block details.|
| /get_timestamp  | POST|To get the mining timestamp of a particular block.|

