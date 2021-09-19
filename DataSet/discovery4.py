# Device data for Alexa discovery - MariaDB version; duplicate records are avoided by using upsert 
# Uses DataSet - a simple data abstraction layer over SQLAlchemy
# https://dataset.readthedocs.io/en/latest/
# MySQL/MariaDB driver work around:
# https://stackoverflow.com/questions/53024891/modulenotfounderror-no-module-named-mysqldb

# pip install dataset

import pymysql
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset

#-----------------------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------------------

# format of database url is "dialect://user:password@host:port/dbname" 
#db = dataset.connect ('sqlite:///temp.db')  # triple slash to denote it is on the local folder
#db = dataset.connect ('sqlite:///:memory:') # ephemeral; useful for testing
db = dataset.connect() # setup an environment variable named DATABASE_URL (defaults to :memory:)
# 'customers' database should already exist; DataSet library cannot create it programmatically
#db = dataset.connect ("mysql://user:passwd@100.101.102.103:3306/customers")   
print (type(db)) 

device_table = None
#-----------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------

def check_tables (table_name):
    tabs = db.tables
    print ('Existing tables:')
    print (tabs)
    print (type(tabs))  # list
    print (len(tabs), ' tables found') 
    if (table_name in tabs):   # NOTE: table name is case sensitive *
        print (table_name, ' table found!')
    else:
        print (table_name, ' table is not found. creating..')
        return False
    return True
    
    
def add_data():
    # dictionary
    dev1 = dict(intofid='INTOF-id-100', endpoint='ABC123.POWER1',  fname='kitchen light')
    dev2 = {'intofid' : 'INTOF-id-100', 'endpoint':'ABC123.POWER2', 'fname':'bedroom light'}
    dev3 = {'intofid' : 'INTOF-id-200', 'endpoint':'DEF456.POWER1', 'fname':'portico'}
    dev4 = {'intofid' : 'INTOF-id-300', 'endpoint':'GHI321.POWER1', 'fname':'coffee'}
    dev5 = {'intofid' : 'INTOF-id-300', 'endpoint':'GHI321.POWER2', 'fname':'fan'}
    
    device_table.insert (dev1)
    device_table.insert (dev2)
    device_table.insert (dev3)
    device_table.insert (dev4)
    device_table.insert (dev5)
    print ('5 devices added.')
 
 
def print_all_data():
    print ('Your data:')
    for row in device_table:  # the table object has a built in iterator. Cool!
        print ('{}] {}\t{}\t{}'.format(row['id'],row['intofid'],row['endpoint'],row['fname']))
    print ('Total rows: ', len(device_table))
    print ('-'*25) 
    
    
def print_stats():
    # Get all table names
    print ('Tables in the db:')
    print (db.tables)
    # Number of rows
    print ('Row count: ', len(device_table))
    # Get columns
    print ('Columns in the table:')
    print(device_table.columns)
    print ('-'*25)    
    
    
def print_filtered_data (data):
    count = 0
    print (type(data))  # this may be a result iterator (possibly, of length 0,1 or more)
    print (data)        # if data is a collection object, you have to iterate through it
    if isinstance (data, dataset.util.ResultIter):
        for d in data:
            print (d)
            count += 1
    elif isinstance (data, OrderedDict):
        count = 1
    print ('Filtered rows: ', count)
    print ('-'*25)
    return count    
#-----------------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------------
    
table_found = check_tables ('device') 

# if the device table is not there, this will create it
device_table = db['device']  
print (type(device_table))

if (not table_found):
    add_data()

# Read data
print_all_data()

# use 'intofid' and 'endpoint' as a compound search key and update that single row (VARIFY this!)
device_table.update (dict(intofid='INTOF-id-100', endpoint='ABC123.POWER2', fname='heater'), ['intofid', 'endpoint'])
print ('Device 100 updated.')

# Update the endpoint itself, even though it is part of the search key:
data = device_table.find_one (intofid='INTOF-id-200', endpoint='DEF456.POWER1')
print (data)
print (len(data), ' fields')
if ('id' in data):  # existence test!
    target_id = data['id']
    device_table.update (dict(id=target_id, endpoint='XYZ007.POWER1'), ['id'])
    print ('Device end point updated.')
else:
    print ('The device does not exist.')
    
print ('Trying to update a non existent device...')
device_table.update (dict(intofid='INTOF-id-900', endpoint='PQR123.POWER1', fname='cooler'), ['intofid', 'endpoint'])
print ('Done! nothing happened.')

print ('After updates:')
print_all_data()

# Now that you have uploaded some data, get the stats of the table
print_stats()
    
# Filters   
print ('Searching for a list of intof devices:')
data = device_table.find (intofid=['INTOF-id-200', 'INTOF-id-100'])  
print_filtered_data (data)
    
print ('Searching for a non-existent device:')
data = device_table.find (intofid=['INTOF-id-900', 'INTOF-id-1000'])  
num_rows = print_filtered_data (data)
if (num_rows==0):
    print ('No records found.')
    
print ('Searching for partially existent devices..')    
data = device_table.find (intofid=['INTOF-id-100', 'INTOF-id-900'])  
print_filtered_data (data)
    
print ("All Intofians:")
data = device_table.find (intofid={'like': 'INTOF%'})
print_filtered_data (data)

 
