import json
import secret
import requests
import pprint
import mysql.connector


API_KEY = secret.FMP_API_KEYS
DB_PW = secret.DB_PASSWORDD


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=DB_PW,
    database="fmp"
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE IF NOT EXISTS fmp")

# mycursor.execute("USE fmp")

# mycursor.execute("CREATE TABLE IF NOT EXISTS company_profile (name VARCHAR(255), symbol VARCHAR(20), exchange VARCHAR(255), sector VARCHAR(255), industry VARCHAR(255), marketCap int)")


# mycursor.execute("ALTER TABLE company_profile ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")

# mycursor.execute("ALTER TABLE company_profile ADD COLUMN numEmployees INT")

def company_profile(symbol: str):

    data = requests.get(f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY}").json()
    data = data[0]
    pprint.pprint(data)

    name = data['companyName']
    symbol = data['symbol']
    exchange = data['exchangeShortName']
    sector = data['sector']
    industry = data['industry']
    marketCap = data['mktCap']
    numEmployees = data['fullTimeEmployees']

    sql = "INSERT INTO company_profile (name, symbol, exchange, sector, industry, marketCap, numEmployees) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (name, symbol, exchange, sector, industry, float(marketCap), int(numEmployees))

    mycursor.execute(sql,val)

    mydb.commit()



if __name__ == '__main__':

    mycursor.execute("ALTER TABLE company_profile MODIFY COLUMN marketCap float")

    company_profile('aapl')


