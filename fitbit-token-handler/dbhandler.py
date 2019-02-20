import mysql.connector
from datetime import datetime

# CREDENTIALS
credentials = open('credentials-db.data', 'r').read().split('\n')
user = credentials[0]
password = credentials[1]

# MYSQL CONNECTION
cnx = mysql.connector.connect(user=user, database='fitbittokens', password=password)
cursor = cnx.cursor(buffered=True)

# BASIC QUERIES

query_add = ("INSERT IGNORE INTO fitbittokens (userid, access_token, refresh_token, expires_in, datetime) VALUES (%s,%s,%s,%s,%s)")


def add(row):
    return "d"