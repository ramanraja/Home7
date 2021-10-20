# Backend code to add Intof customers to the Intof database
 
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

class UserRegistration ():

    def __init__ (self, database):
        self.db = database
        self.table_name = 'registration'   # it is case sensitive *
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
                     
    def get_user (self, intof_id):
        record = self.table.find_one (intofid=intof_id) # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'intofid' not in record):
            return None
        return record # This always returns a singleton  
              
        
    def create_user (self, user): 
        print ('Adding a new user: ', user)
        if  'intofid' not in user:
            iid = self.create_intof_id()
        else:
            iid = user.get('intofid')
        if  'password' not in user:
            passwd = self.create_default_password()
        else:
            passwd = user.get('password') 
        name = user.get('name', 'Anonymous')
        mail = user.get ('email', 'user@example.com')
        phash =  self.create_password_hash (passwd)
        user_record = {'intofid' : iid, 'email' : mail, 'name' : name, 'passhash' : phash}
        self.table.insert (user_record)
    
    def create_intof_id (self):
        r = randint(100,10000)  # TODO: implement this
        iid = 'INTOF-id-' +str(r)
        return (iid)
        
    def create_default_password (self):
        return  ('Your-Default-Password')  # TODO: implement randomized password
        
    def create_password_hash  (self, passwd):
        return (passwd[::-1])           # TODO: implement
    
    # ---------------- utility helpers ------------------------------------------
        
    def add_test_data (self):
        usr1 = dict(intofid='INTOF-id-100',  email='raja@raman.com', name='Raman Raja', passhash='ACASDFK234ASDFO09')
        usr2 = {'intofid' : 'INTOF-id-200', 'email' : 'jara@maran.com', 'name' : 'Jara Maran', 'passhash' : 'TT4894KI40XX'}
        usr3 = {'intofid' : 'INTOF-id-300', 'email' : 'kittu@mama.com', 'name' : 'Kittu Mama', 'passhash' : 'YY90UI34KJ5R'}
        usr4 = {'intofid' : 'INTOF-id-999', 'email' : 'pattu@mami.com', 'name' : 'Pattu Mami', 'passhash' : 'XX6996XX6996'}
        self.table.insert (usr1)
        self.table.insert (usr2)
        self.table.insert (usr3)
        self.table.insert (usr4)
        print ('4 test users added.')
    
    
    def print_all_data (self):
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  ({}) {} -> {}, {} [{}]'.format(row['id'], row['intofid'],row['email'],row['name'],row['passhash']))  #[:10]))
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

    regn = UserRegistration (db)
    
    # You must always call setup(). This is where the table is created
    table_exists = regn.setup() 
    
    if (not table_exists):
        print ('User mapping table not found. Creating test entries anyway..')
        regn.add_test_data()
    print()
        
    usr = {
        'name' : 'Apputtu',
        'age' : 11
    }    
    regn.create_user (usr)
    print()
        
    regn.print_all_data()
    print()
    regn.print_stats()
    print()
    
    # Filter   
    iid = 'INTOF-id-300'
    print ('Searching for Intof id: ',iid)
    user = regn.get_user (iid)
    print ('User profile:')
    print (user)
    print()
        
    print ('Searching for non-existent user:')
    user = regn.get_user ('None-Such')
    print ('User profile:')
    print (user)
    print()
