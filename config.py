from flask import Flask, request, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, JSON, MetaData, update, create_engine, DateTime, Boolean, func


app = Flask(__name__)
engine = create_engine('sqlite:///tasks_db', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
Base = declarative_base()
session = Session()

class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=func.now())
    time_execute = Column(Integer)
    mail = Column(String)
    done = Column(Boolean, default=False)
    params = Column(String)
    result = Column(String)

    def __init__(self, params, mail=None):
        self.params = params


func_map = {'multiprint': 'multi_print',
            'mult': 'mult'}

Base.metadata.create_all(engine)



