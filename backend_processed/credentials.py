
import os 


class Credentials:
    def __init__(self):
        credentials_db = open('credentials-db.data', 'r').read().split('\n')
        self.user = credentials_db[0]
        self.password = credentials_db[1]   
    


if __name__=="__main__":
    credentials = Credentials()
    print(f"user: {credentials.user}, password:{credentials.password}")