from flask import Flask, request, render_template
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, JSON, MetaData, update, create_engine, DateTime, Boolean, func


app = Flask(__name__)





