import os
        
class Config (object):
    APP_PORT = os.environ.get ('APP_PORT') or 5000
    SESSION_TYPE = 'filesystem' 
    SECRET_KEY = os.environ.get ('SECRET_KEY') or 'secret_key'    
    #DATABASE_URL = 'mysql://user:passwd@13.140.150.160:3306/customers'
    #DATABASE_URL = 'sqlite:///temp.db'
             
    TEMPLATES_AUTO_RELOAD = True    
    
    USE_AUTH_HEADER = True  # True=use header; False=use cookies
    TOKEN_ID = 'x-access-token'
    
    DPRINT_ENABLED = True
    #---------------------------------------------------------------------------
    # Static helper method
    def dump ():    
        print ('\nConfig:') 
        if Config.USE_AUTH_HEADER: 
            print ('Using HTTP header for authentication')
        else:
            print ('Using cookies for authentication')
        print ('APP_PORT: %d [%s]' %(Config.APP_PORT, type(Config.APP_PORT)))
        print ('DATABASE_URL: %s' % Config.DATABASE_URL)
        print ('SESSION_TYPE: %s' % Config.SESSION_TYPE)
        print ('SECRET_KEY: %s' %'*****')  # Config.SECRET_KEY)
        print ('DPRINT_ENABLED: %s' % Config.DPRINT_ENABLED)
        print()        
        
 