from flask import current_app as app  
from flask import Flask
from flask_cors import CORS
from random import randint
from time import sleep
import json
from collections import OrderedDict
import dataset
import pymysql
pymysql.install_as_MySQLdb()    # this is a workaround to make pymysql work with Python 3.x
from intof.registration import UserRegistration     ## NOTE THE INTOF-DOT !
from intof.relsen import RelsenMap
from intof.devices import DeviceMap
from config import Config

print ("Running Module: ", __name__)   
print ('At the top level.')
Config.dump()

#------------------------------------------------------------------------------------------
print ('initializing database..') 

# format of database url is "dialect://user:password@host:port/dbname" 
# The following enviroment variable is to be set if you specify 'None' for database_url:
# SET DATABASE_URL=sqlite:///temp.db

#database_url = None                        # set the URL in the environment
#database_url = 'sqlite:///temp.db'         # local file
#database_url = 'sqlite:///:memory:'        # ephemeral; useful for testing
database_url = Config.DATABASE_URL          # take it directly from config.py file, not app.config

print ('Using database: ', database_url)

if database_url:
    db = dataset.connect (database_url) 
else:
    db = dataset.connect()  # setup an environment variable named DATABASE_URL (defaults to :memory:)

user_reg = UserRegistration (db)
# You must always call setup(). This is where the table is created
table_exists = user_reg.setup() 
if (not table_exists):
    print ('User registration table not found. Creating test entries anyway..')
    user_reg.add_test_data()
print ('UserRegistration initialized.')
    
device_reg = RelsenMap (db)
# You must always call setup(). This is where the table is created
table_exists = device_reg.setup() 
if (not table_exists):
    print ('Device config table not found. Creating test entries anyway..')
    device_reg.add_test_data() 
print ('Device registration initialized.')

device_map = DeviceMap (db)
# You must always call setup(). This is where the table is created
table_exists = device_map.setup() 
if (not table_exists):
    print ('Device Mapping table not found. Creating test entries anyway..')
    device_map.add_test_data() 
print ('Device-user map initialized.')

print ('Database initialion completed.')
#------------------------------------------------------------------------------------------
        
def create_my_app ():
    app = Flask (__name__)
    print ('Configuring app..')     
    with app.app_context():
        app.config.from_object (Config)
        CORS (app)
        from . import router     # imported within the app context
        #from .registration import UserRegistration
        #from .relsen import RelsenMap
        print ('initialization completed.') 
        return (app)
    