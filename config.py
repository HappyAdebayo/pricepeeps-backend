import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="pricepeepsdb",
        user="postgres",
        password="adeyanju#2005"
    )
