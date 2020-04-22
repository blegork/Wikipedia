import MySQLdb


class Connection:

    def __init__(self):
        self.db = None

    def query_request2(self, query, values):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def open(self, db, host, user, password):
        self.db = MySQLdb.connect(host=host, user=user, passwd=password, db=db)
        self.cursor = self.db.cursor()

    def close(self):
        if self.db is not None: self.db.close()

