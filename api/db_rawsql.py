from MySQLdb import ProgrammingError
from sqlalchemy import create_engine
from sqlalchemy.ext.sqlsoup import SqlSoup
from api.setttings import *

def raw_sql(sql):
    engine = create_engine('mysql://%s:%s@%s/%s' % \
        (CLOUD_MONITOR_MYSQL_USERNAME,CLOUD_MONITOR_MYSQL_PASSWORD,CLOUD_MONITOR_MYSQL_HOST,CLOUD_MONITOR_MYSQL_DB))
    db = SqlSoup(engine)
    return db.execute(sql).fetchall()
