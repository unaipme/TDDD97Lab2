from __future__ import print_function
import sys
import sqlite3
from sqlite3 import IntegrityError, OperationalError
from flask import g
from enum import Enum

class ErrNo(Enum):
    NO_ERROR = -1       # No error
    UNKNOWN = 0         # Unknown error
    QUERY_ERR = 1       # Query not generated properly
    EX_DATA_ERR = 2     # Existing data error

ERROR_MSG = {ErrNo.EX_DATA_ERR: "The same data already existed in the database",
             ErrNo.QUERY_ERR: "The query wasn't generated properly",
             ErrNo.UNKNOWN: "Unknown error occurred",
             ErrNo.NO_ERROR: "Everything went right"}


def printc(txt):
    print(txt, file=sys.stderr)


def createjson(attnames, values):
    ret = {}
    if len(values) != len(attnames):
        raise AssertionError
    for i in range(0, len(attnames)):
        ret[attnames[i]] = values[i]
    printc(ret)
    return ret


class DatabaseHelper(object):

    def __init__(self, dbname):
        self.__dbname = dbname
        c = self.__get_db()
        if str(c.execute("select sql from sqlite_master where type = 'table'").fetchall()) == "[]":
            f = open("./static/database.sql", "r")
            schema = ""
            for line in f:
                schema += line
            f.close()
            c.executescript(schema)
            c.commit()
        else:
            printc("Everything's ready\n")
        self.__close()

    def __get_db(self):
        db = getattr(g, "db", None)
        if db is None:
            db = g.db = sqlite3.connect(self.__dbname)
        return db

    def __close(self):
        self.__get_db().close()

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
        c = self.__get_db()
        try:
            sqlst = "INSERT INTO " + tablename + " " + str(collist) + " VALUES " + str(valuelist)
            c.execute(sqlst)
        except IntegrityError:
            c.rollback()
            resp = createjson(("success", "message", "errno"), (False, ERROR_MSG[ErrNo.EX_DATA_ERR], ErrNo.EX_DATA_ERR))
        except OperationalError:
            c.rollback()
            resp = createjson(("success", "message", "errno"), (False, ERROR_MSG[ErrNo.QUERY_ERR], ErrNo.QUERY_ERR))
        except Exception:
            c.rollback()
            resp = createjson(("success", "message", "errno"), (False, ERROR_MSG[ErrNo.UNKNOWN], ErrNo.UNKNOWN))
        else:
            c.commit()
            resp = createjson(("success", "message", "errno"), (True, ERROR_MSG[ErrNo.NO_ERROR], ErrNo.NO_ERROR))
        finally:
            self.__close()
        return resp
