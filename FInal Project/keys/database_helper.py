from django.db import connection

def get_all_states():
    with connection.cursor() as cursor:
        cursor.execute("SELECT  * FROM states")
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


