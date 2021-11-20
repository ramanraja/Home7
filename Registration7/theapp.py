###from intof import app
from flask import Flask
from intof import create_my_app
from time import sleep
import sys

def cleanup():
    print ('\n* Main thread exits!')
    
app = create_my_app()  # app factory

if __name__ == "__main__": 
    PORT =  app.config['APP_PORT']
    print ('Starting registration server on port {}...'.format (PORT))
    try:
        app.run(host='0.0.0.0', port=PORT)  #, use_reloader=False, debug=False) 
    except KeyboardInterrupt:
        print ('^C received.')
    cleanup()
        