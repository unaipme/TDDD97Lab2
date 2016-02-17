import sqlite3
from flask import g


class DatabaseHelper(object):

    def __init__(self, dbname):
        self.__conn = sqlite3.connect(dbname)


    def select(self, collist, tablename, more=""):
        sqlst = "SELECT "
        for i in range(0, len(collist)):
            sqlst += collist[i]
            if i < len(collist) - 1:
                sqlst += ", "
        print sqlst + more
