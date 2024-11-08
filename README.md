# INS Assigment 
## Topic: Symmetric Key Distribution using KDC

A terminal based application to simulate an approach for communications between different clients using a Key Distribution Center (KDC) implementing symmetric key distribution ( Diffie-Helman).

## How to run the application

```bash
 pip install -r requirements.txt 
 ```

```  bash
python3 key_distribution_center.py 
```

For each client create new terminal

``` bash
python3 client.py 
```

## Commands
- password = "password" (for authentication)
- client_list : To get the addresses of all the authenticated clients other than current one.
- REQUEST_CONNECTION:"address of client"
- START_COMMUNICATION:"address of client"
- MESSAGE:"address of client":"message to be sent"