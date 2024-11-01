from mysql import MySQLManager

db = MySQLManager(
                host= "localhost",
                port= "3306",
                user = "root",
                password="admin",
)

db.connect()