from datetime import datetime

import fire

from clients import client_map
from db import ClientUser

client_codes = [client.code for client in client_map.values()]

def main(email: str, client: str, credits: int):
    user = ClientUser.select(email=email, client=client).one()
    if not user:
        print("User Not Found")
        return
    
    user.credits += credits
    user.credits_last_used = datetime.now()
    user.save()
    
    print(f'{credits} credits added')
    print(f'User now has {user.credits} credits')

        
if __name__ == "__main__":
    fire.Fire(main)