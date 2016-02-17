from __future__ import print_function
import sys
import sqlite3
from flask import g

def printc(txt):
    print(txt, file=sys.stderr)


class DatabaseHelper(object):

    def __init__(self, dbname):
        self.__dbname = dbname
        self.__createcursor()
        # printc(str(self.__execute("select sql from sqlite_master where type = 'table'")))
        if str(str(self.__execute("select sql from sqlite_master where type = 'table'"))) == "[]":
            f = open("./static/database.sql", "r")
            schema = ""
            for line in f:
                schema += line
            f.close()
            self.__c.executescript(schema)
        else:
            printc("Everything's ready\n")
        self.__closecursor()

    def __createcursor(self, dbname=None):
        if dbname is None:
            dbname = self.__dbname
        self.__conn = sqlite3.connect(dbname)
        self.__c = self.__conn.cursor()

    def __closecursor(self):
        self.__c.close()
        self.__conn.close()

    def __execute(self, sql):
        result = self.__c.execute(sql).fetchall()
        self.__conn.commit()
        return result

    def select(self, collist, tablename, more=""):
        '''
        sqlst = "SELECT "
        for i in range(0, len(collist)):
            sqlst += collist[i]
            if i < len(collist) - 1:
                sqlst += ","
            sqlst += " "
        sqlst += "FROM " + tablename + " "
        printc(sqlst + more)
        '''
        sqlst = "SELECT " + str(collist).lstrip("(").rstrip(")") + " FROM " + tablename
        if more != "":
            sqlst += " " + more
        printc(sqlst)

    def insert(self, tablename, collist, valuelist):
        sqlst = "INSERT INTO " + tablename + " " + str(collist) + " VALUES " + str(valuelist)
        self.__createcursor()
        self.__execute(sqlst)
        self.__closecursor()
        # printc(sqlst)
