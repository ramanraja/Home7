# Backend code to add 'devices' to the Intof database
# NOTE: Each individual relay or sensor is called a 'device' in the user parlance, but it is internally called a 'Relsen'.
 
# pip install dataset

# TODO: API for insert, update, delete
# TODO: factor out the common code to a base class (feature:instead of iterator, bulk downloads as a list)

from urllib.request import urlopen
from collections import OrderedDict
import pymysql
from random import randint
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset
import json

#---------------------------------------------------------------------------------------------------------------

class RelsenMap ():

    def __init__ (self, database):
        self.db = database
        self.table_name = 'relsen'   # it is case sensitive *
        self.table = None 
             
             
    def setup (self): # You MUST call this function immediately after creating this object
        tabs = self.db.tables
        print ('Existing tables: ', tabs)
        # if the table is present, open it, otherwise create a new table:
        self.table = self.db[self.table_name] 
        if (not self.table_name in tabs):   
            print (self.table_name, ' table not found!')
            return False
        print (self.table_name, ' table found.')
        return True
    
    
    # The table has one-to-many mapping: for each intofid there are a number of relsens
    '''                 
    def get_user (self, intof_id):
        record = self.table.find_one (intofid=intof_id) # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'intofid' not in record):
            return None
        return record # This always returns a singleton  
    '''          
        
    def get_user_relsens (self, intof_id):
        recordset = self.table.find (intofid=intof_id) # returns None if no recrod is found
        print (recordset)
        if recordset is None:
            return None
        else:
            print (type(recordset))
        return recordset   
        
                
    def create_relsen (self, intof_id, end_point, friendly_name):  
        print ('Adding new relsen: ', end='')
        if  friendly_name is None or len (friendly_name)==0:
            err = 'Alexa name is missing'
            return (False, err)        
        relsen_record = {'intofid' : intof_id, 'endpoint' : end_point, 'fname' : friendly_name}
        print (relsen_record)
        try:
            self.table.insert (relsen_record)  
        except Exception as e:
            return (False, str(e))
        return (True, 'Relsen added.')
        

    def add_device (self, device):
        print ('Adding device: ', device)
        intof_id = device.get('intof_id')
        if  intof_id is None or len (intof_id)==0:
            err = 'User ID is missing'
            return (False, err)
        device_id = device.get('device_id')
        if  device_id is None or len (device_id)==0:
            err = 'Device ID is missing'
            return (False, err) 
        end_point = '{}.POWER{}'.format(device_id, str(1)) # TODO: make this flexible using an array of 1 to 8 relays and also handle sensors
        result = self.create_relsen (intof_id, end_point, device['relsens']['relay1']) 
        print (result)
        if not result[0]: return result
        end_point = '{}.POWER{}'.format(device_id, str(2))
        result = self.create_relsen (intof_id, end_point, device['relsens']['relay2']) 
        print (result)
        if not result[0]: return result        
        end_point = '{}.POWER{}'.format(device_id, str(3))
        result = self.create_relsen (intof_id, end_point, device['relsens']['relay3']) 
        print (result)
        if not result[0]: return result        
        end_point = '{}.POWER{}'.format(device_id, str(4))
        result = self.create_relsen (intof_id, end_point, device['relsens']['relay4'])  
        print (result)
        return result
        
    # ---------------- utility helpers ------------------------------------------
        
    def add_test_data (self):
        dev1 = {
            'intof_id' : 'IN-1234', 'device_id' : 'TOF-ABC123', 'relsens' : 
            {'relay1' : 'tube light', 'relay2' : 'fan', 'relay3' : 'kitchen light', 'relay4' : 'AC' }
        }
        dev2 = {
            'intof_id' : 'IN-4321', 'device_id' : 'TOF-DEF321', 'relsens' : 
            {'relay1' : 'portico lamp', 'relay2' : 'bedroom', 'relay3' : 'coffe maker', 'relay4' : 'desk lamp' }
        }
        self.add_device (dev1)
        self.add_device (dev2)
        print ('2 test devices added.')
    
    
    def print_all_data (self):
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  ({}) {} -> {} [{}]'.format(row['id'], row['intofid'],row['endpoint'],row['fname'])) 
        print ('Total rows: ', len(self.table))
        #print ('-'*25)
    

    def print_filtered_data (self, data):
        count = 0
        #print (type(data))  # this may be a result iterator (possibly, of length 0,1 or more)
        if isinstance (data, dataset.util.ResultIter):
            for d in data:
                print (d)
                count += 1
        elif isinstance (data, OrderedDict): # A single record was returned
            print (data)
            count = 1
        print ('Filtered rows: ', count)
        #print ('-'*25)
        return count   # NOTE: Now we have reached the end of the iterator, so it cannot be used again *
        

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
    #database_url = 'mysql://user:passwd@103.104.105.106:3306/customers'  # 'customers' database should already exist 
    
    if database_url:
        db = dataset.connect (database_url) 
    else:
        db = dataset.connect()  # setup an environment variable named DATABASE_URL (defaults to :memory:)

    relsen_map = RelsenMap (db)
    
    # You must always call setup(). This is where the table is created
    table_exists = relsen_map.setup() 
    
    if (not table_exists):
        print ('Relsen mapping table not found. Creating test entries anyway..')
        relsen_map.add_test_data()
    print()
        
    dev = {
        'intof_id' : 'IN-00101', 'device_id' : 'TOF-XYZ000', 'relsens' : 
        {'relay1' : 'table lamp', 'relay2' : 'table fan', 'relay3' : 'portico light', 'relay4' : 'power plug' }
    }
    relsen_map.add_device (dev)
    print()
        
    relsen_map.print_all_data()
    print()
    relsen_map.print_stats()
    print()
    
    # Filter   
    iid = 'IN-00101'
    print ('Searching for Intof id: ',iid)
    rels = relsen_map.get_user_relsens (iid)
    print ('Users relsens:')
    relsen_map.print_filtered_data (rels)
    print()
        
    print ('Searching for non-existent user:')
    user = relsen_map.get_user_relsens ('None-Such')
    print ('Users relsens:')
    relsen_map.print_filtered_data (rels)
    print()