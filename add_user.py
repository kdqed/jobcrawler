import fire

from clients import client_map
from db import ClientUser

client_codes = [client.code for client in client_map.values()]

def main(name: str, email: str, client: str):
    if client not in client_codes:
        print('Invalid Client')
        return
    
    result = ClientUser.add(name, email, client)
    if result:
        print('User Added')
    else:
        print('User Already Exists')

        
if __name__ == "__main__":
    fire.Fire(main)