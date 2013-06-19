#!/usr/bin/env python
import datetime
from setttings import *
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Instances(Base):
    __tablename__="nova_instances"
    
    id=Column(Integer,primary_key=True, autoincrement=True)
    physical_host = Column(String(128), nullable=True)
    ip_address = Column(String(128), nullable=True)
    name = Column(String(64), nullable=True)
    state = Column(String(32), nullable=True)
    uuid = Column(String(128), nullable=True)
    moniting_state = Column(String(1024), nullable=True)
    notification_state = Column(String(1024), nullable=True)
    last_update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __init__(self,ip_address=None, name=None, uuid=None, state=None,
                 moniting_state=None, notification_state=None, physical_host=None):
        self.physical_host = physical_host
        import simplejson
        if not ip_address: ip_address = None
        self.ip_address = simplejson.dumps(ip_address)
        self.name = name
        self.uuid = uuid
        self.state = state
        self.moniting_state = moniting_state
        self.notification_state = notification_state
    
    def __repr__(self):
        return "<Instance('%s','%s','%s','%s')" % (self.ip_address, self.name, self.state, self.last_update_time)

instances_table = Instances.__table__
metadata = Base.metadata


engine = create_engine("mysql://%s:%s@%s/%s" % (MYSQL_USERNAME,MYSQL_PASSWORD,MYSQL_HOST,MYSQL_DB),
                       echo=False, convert_unicode=True, encoding='utf-8')
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    metadata.create_all(engine)
