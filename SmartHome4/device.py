# Device data for Alexa discovery - using MariaDB   
# Get all the end points and the Alexa-friendly names of devices owned by a given Intof-User-ID 
# pip install dataset


# TODO: API for insert, update, delete
# TODO: factor out the common code to a base class (feature:instead of iterator, bulk downloads as a list)


import pymysql
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
from collections import OrderedDict
import dataset
import json
 
#-----------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------

class Device ():

    def __init__ (self, database):
        self.db = database
        self.table_name = 'device'   # it is case sensitive *
        self.table = None 
        
            
    # You MUST call setup() immediately after creating a Device object:
    # This is where the table is created or initialized
    def setup (self): 
        tabs = self.db.tables
        print ('Existing tables: ', tabs)
        # if the table is present, open it, otherwise create a new table:
        self.table = self.db[self.table_name] 
        if (not self.table_name in tabs):   
            print (self.table_name, ' table not found!')
            return False
        print (self.table_name, ' table found')
        return True
 
    
    def add_test_data (self):
        # input can be dictionary or json
        dev1 = dict (intofid='INTOF-id-100', endpoint='ABC123.POWER1',  fname='kitchen light')
        dev2 = {'intofid' : 'INTOF-id-100', 'endpoint':'ABC123.POWER2', 'fname':'bedroom light'}
        dev3 = {'intofid' : 'INTOF-id-200', 'endpoint':'DEF456.POWER1', 'fname':'portico'}
        dev4 = {'intofid' : 'INTOF-id-300', 'endpoint':'GHI321.POWER1', 'fname':'coffee'}
        dev5 = {'intofid' : 'INTOF-id-300', 'endpoint':'GHI321.POWER2', 'fname':'fan'}
        dev6 = {'intofid' : 'INTOF-id-999-RR', 'endpoint':'intof_FF6CD8.POWER1', 'fname':'room heater'}
        self.table.insert (dev1)
        self.table.insert (dev2)
        self.table.insert (dev3)
        self.table.insert (dev4)
        self.table.insert (dev5)
        self.table.insert (dev6)
        self.table.insert (dev11)         
        print ('6 test devices added.')
 
    
    def get_devices (self, intof_id):
        data = self.table.find (intofid=intof_id)
        retval = []
        for d in data:
            relay = tuple ((d['endpoint'], d['fname']))  # A tuple is ordered and unmutable
            retval.append (relay)
        return (retval)  # this can be an empty list also
 
    # ---------------- utility helpers ------------------------------------------
         
    def print_all_data (self): # dump the table
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  {}) {}\t{}\t{}'.format(row['id'],row['intofid'],row['endpoint'],row['fname']))
        print ('Total rows: ', len(self.table))
        #print ('-'*25) 
     
    
    def print_filtered_data (self, data):
        count = 0
        #print (type(data))  # this may be a result iterator (possibly, of length 0,1 or more)
        print (data)        # if data is a collection object, you have to iterate through it
        if isinstance (data, dataset.util.ResultIter):
            for d in data:
                print (d)
                count += 1
        elif isinstance (data, OrderedDict):
            print (data)
            count = 1
        print ('Filtered rows: ', count)
        #print ('-'*25)
        return count    # NOTE: Now we have reached the end of the iterator, so it cannot be used again
    
    
    def print_stats (self):
        # Get all table names
        print ('Tables in the db:')
        print (self.db.tables)
        print ('Your table is: ', self.table)
        # Number of rows in our table of interest
        print ('Rows in your table: ', len(self.table))
        # Get columns
        print ('Columns in your table:')
        print(self.table.columns)
        #print ('-'*25)       
#-----------------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------------

if (__name__ == '__main__'): 

    # format of database url is "dialect://user:password@host:port/dbname" 
    database_url = None
    #database_url = 'sqlite:///temp.db'              # local file
    #database_url = 'sqlite:///:memory:'             # ephemeral; useful for testing
    #database_url = 'mysql://user:passwd@100.101.102.103:3306/customers'  # 'customers' database should already exist 
    print ('Using Database: ', database_url)

    if database_url:
        db = dataset.connect (database_url) 
    else:
        db = dataset.connect()  # setup an environment variable named DATABASE_URL (defaults to :memory:)
    device = Device (db)
    # You must always call setup(). This is where the table is created
    table_exists = device.setup() 
    print()
        
    if (not table_exists):
        print ('Device table not found. Creating test entries anyway..')
        device.add_test_data()
        print()
            
    device.print_all_data()
    print()
    device.print_stats()
    print()
        
    # Filter   
    print ('Searching for devices of INTOF-id-100..')
    devs = device.get_devices ('INTOF-id-100')
    #device.print_filtered_data (devs) # this will take the iterator to its end, so it cannot be used again!
    print (devs)
    print (len(devs), ' relays.')    
    print()
    
    print ('Searching for devices of non-existent user..')
    devs = device.get_devices ('Not-A-User')
    print (devs)
    print (len(devs), ' relays.')    
    print()
   
    print ('Searching for a singleton record..')
    devs = device.get_devices ('INTOF-id-200')
    print (devs)
    print (len(devs), ' relays.')    
    print()    
 
    print ('Searching for devices of a real Alexa user..')
    devs = device.get_devices ('INTOF-id-999-VR')
    print (devs)
    print (len(devs), ' relays.')    
    print()  
 

'''----------------------------------------
UPDATES  (TODO: implement these ! - this class serves only discovery; you need another full 'Device' class)
-------
# use 'intofid' and 'endpoint' as a compound search key and update that single row (VARIFY this!)
device_table.update (dict(intofid='INTOF-id-100', endpoint='ABC123.POWER2', fname='heater'), ['intofid', 'endpoint'])
print ('Device 100 updated.')

# Update the endpoint itself, even though it is part of the search key:
data = device_table.find_one (intofid='INTOF-id-200', endpoint='DEF456.POWER1') # find_one() returns None if record is not found *
print (data)
if (data is None or 'id' not in data):   # existence test!
    print ('The device does not exist.')
else:
    print (len(data), ' fields')
    target_id = data['id']
    device_table.update (dict(id=target_id, endpoint='XYZ007.POWER1'), ['id'])
    print ('Device end point updated.')
    
print ('Trying to update a non existent device...')
device_table.update (dict(intofid='INTOF-id-900', endpoint='PQR123.POWER1', fname='cooler'), ['intofid', 'endpoint'])
print ('Done! nothing happened.')

print ('After updates:')
print_all_data()

------------------------------------------'''
 
