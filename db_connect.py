import pymysql
from config import host, user, password, db_name


# Обработка sql запроса
def dbinf(sql):
    # sql = "CREATE TABLE Posts (id INT NOT NULL AUTO_INCREMENT, heading VARCHAR(20), hashteg VARCHAR(20), text TEXT, date DATETIME, PRIMARY KEY ( id ));"
    try:

        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        try:

            with connection.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                connection.commit()
                return rows

        finally:
            connection.close()

    except Exception as ex:
        print("Connection refused...")
        print(ex)
