# Amazon ID to Intof ID mapping; Grant code and token added
# Support added for exchanging Alexa token for Amazon User ID
# An Amazon web service accepts the token and returns the Amazon-User-ID of the Alexa account
# In turn, we map it to an Intof-User-ID from our MariaDB database
# pip install dataset


# TODO: API for insert, update, delete
# TODO: factor out the common code to a base class (feature:instead of iterator, bulk downloads as a list)


from urllib.request import urlopen
from collections import OrderedDict
import pymysql
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset
import json

#---------------------------------------------------------------------------------------------------------------

class UserMap ():

    def __init__ (self, database):
        self.db = database
        self.table_name = 'usermap'   # it is case sensitive *
        self.table = None 
        self.amazon_token_base_url = "https://api.amazon.com/user/profile?access_token="     
             
             
    def setup (self): # You MUST call this function immediately after creating this object
        tabs = self.db.tables
        print ('Existing tables: ', tabs)
        # if the table is present, open it, otherwise create a new table:
        self.table = self.db[self.table_name] 
        if (not self.table_name in tabs):   
            print (self.table_name, ' table not found!')
            return False
        print (self.table_name, ' table found')
        return True


    def amazon_grant_map (self, amazon_id):
        record = self.table.find_one (amazonid=amazon_id) # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'grant_code' not in record):
            return None
        return (tuple((record['grant_code'], record['grant_token'])))  # This always returs a singleton  
        
        
    def intof_grant_map (self, intof_id):
        record = self.table.find_one (intofid=intof_id) # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'grant_code' not in record):
            return None
        return (tuple((record['grant_code'], record['grant_token'])))  # This always returs a singleton  
        
                
    def amazon_intof_map (self, amazon_id):
        record = self.table.find_one (amazonid=amazon_id) # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'intofid' not in record):
            return None
        return record['intofid']  # This always returs a singleton  
         
        
    def token_amazon_map (self, token):
        url = self.amazon_token_base_url + token
        try:
            response = urlopen (url)
            amazonid = response.read().decode('utf-8')
        except Exception as e:
            print ('Cound not retrieve Amazon ID: '+str(e))
            return None
        print ('Amazon user id: ', amazonid) 
        print (type(amazonid))  # it is json 
        jamazonid = json.loads(amazonid)
        return (jamazonid['user_id'])
        
        
    def token_intof_map (self, token):
        amazonid = self.token_amazon_map (token)
        if amazonid is None:
            return None
        intofid = self.amazon_intof_map (amazonid)
        return (intofid)
        
    # ---------------- utility helpers ------------------------------------------
        
    def add_test_data (self):
        usr1 = dict(amazonid='Amazon-id-001', intofid='INTOF-id-100', grant_code='this-is-sample-grant-code1', grant_token='this-is-sample-grant-token-1')
        usr2 = {'amazonid' : 'Amazon-id-002', 'intofid' : 'INTOF-id-200', 'grant_code' : 'this-is-sample-grant-code2', 'grant_token' : 'this-is-sample-grant-token-2'}
        usr3 = {'amazonid' : 'Amazon-id-003', 'intofid' : 'INTOF-id-300', 'grant_code' : 'this-is-sample-grant-code3', 'grant_token' : 'this-is-sample-grant-token-3'}
        usr4 = {'amazonid' : 'amzn1.account.AF4GHQQFG6I776LETS6YCFSCP3UA', 'intofid' : 'INTOF-id-999', 'grant_code' : 'this-is-sample-grant-code4', 'grant_token' : 'this-is-sample-grant-token-4'}
        self.table.insert (usr1)
        self.table.insert (usr2)
        self.table.insert (usr3)
        self.table.insert (usr4)
        print ('4 test users added.')

    
    def print_all_data (self):
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  ({}) {} -> {}   [{}.., {}..]'.format(row['id'], row['amazonid'],row['intofid'],row['grant_code'][:10],row['grant_token'][:10]))
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
        return count   # NOTE: Now we have reached the end of the iterator, so it cannot be used again
        

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
    #database_url = None
    #database_url = 'sqlite:///temp.db'              # local file
    #database_url = 'sqlite:///:memory:'             # ephemeral; useful for testing
    database_url = 'mysql://xxx:yyy@113.105.101.113:3306/customers'  # 'customers' database should already exist 
    
    if database_url:
        db = dataset.connect (database_url) 
    else:
        db = dataset.connect()  # setup an environment variable named DATABASE_URL (defaults to :memory:)

    umap = UserMap (db)
    
    # You must always call setup(). This is where the table is created
    table_exists = umap.setup() 
    
    if (not table_exists):
        print ('User mapping table not found. Creating test entries anyway..')
        umap.add_test_data()
        
    umap.print_all_data()
    umap.print_stats()
    
    # Filter   
    print ('Searching for an Amazon user:')
    user = umap.amazon_intof_map ('Amazon-id-002')
    print ('Intof ID: ', user) 
    print()
        
    print ('Searching for non-existent user:')
    user = umap.amazon_intof_map ('None-Such')
    print ('Intof ID: ', user) 
    print()
    
    print ('Grants for Amazon user:')
    grants = umap.amazon_grant_map ('Amazon-id-002')
    print ('Grants: ', grants) 
    print()
    
    print ('Grants for Intof user:')
    grants = umap.intof_grant_map ('INTOF-id-200')
    print ('Grants: ', grants) 
    print()
        
    #token = 'replace-this-dummy-token-with-the-actual-one'  
    # Say 'Alexa, Switch 2 ON' and then copy this token from Cloud Watch logs
    token = "Atza|Ba9IwEBIEfUf....."

    print ('Getting Intof ID from Alexa token:')
    user = umap.token_intof_map (token)
    print ('Intof ID: ', user) 
