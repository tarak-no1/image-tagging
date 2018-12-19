import pymysql.cursors


config = {
    "host": '35.197.132.215',
    "user": 'root',
    "password": 'MEw9f.YL'
}
def sqlQuery(db_name, query):
	connection = pymysql.connect(host='35.197.132.215',
                             user='root',
                             password='MEw9f.YL',
                             db=db_name,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
	try:
	    with connection.cursor() as cursor:
	        cursor.execute(query)

	    # connection is not autocommit by default. So you must commit to save
	    # your changes.
	    connection.commit()
	finally:
	    connection.close()