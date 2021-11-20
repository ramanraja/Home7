from flask import current_app as app  
 
from flask import request, render_template, session  
from intof.registration import UserRegistration   ## NOTE THE intof. prefix
from intof import user_reg, device_reg, device_map
from random import randint
 
#----------------------------------------------------------------------------------------
# helper methods    
#----------------------------------------------------------------------------------------
DPRINT_ENABLED = True
def dprint (*args):
    #app.logger.info (*args)
    if DPRINT_ENABLED:
        print (*args)
    
#------------------------------------------------------------------------------------------
    
@app.route('/')
def rooot():
    ###return (render_template('login.html'))  
    return (render_template('menu.html')) 

@app.route('/menu')
def menu():
    return (render_template('menu.html')) 
        
        
@app.route('/debug')
def debug_links():
    return (render_template('debug.html')) 
    
            
@app.route('/random', methods =['GET']) 
def random (): 
    return ({'random' : randint(0, 10000)})
        
        
@app.route('/print/stats')
def print_stats():
    user_reg.print_stats()
    device_reg.print_stats()
    print()
    return ({'success' : True, 'msg' : 'printed on console.'})
    
 
@app.route('/get/current/user')
def get_current_user_id():
    usr = session.get('current_user')
    print ('current user:', usr)
    result = True
    if (usr is None): 
        result = False
    return ({'success' : result, 'current_user' : usr})
    

@app.route('/list/all/users')
def dump_all_users():
    user_reg.print_all_data()
    print()
    return ({'success' : True, 'msg' : 'printed on console.'})
    
    
@app.route('/list/all/devices')
def dump_all_relsens():
    device_reg.print_all_data()
    print()
    return ({'success' : True, 'msg' : 'printed on console.'})
    
   
@app.route('/logout')
def logout (): 
    session['current_user'] = None
    return ({'success' : True, 'msg' : 'user logged out.'})
    

# This is a quick and dirty login form, in case there is no real client app
@app.route('/login/form')
def login_form():
    return (render_template('login.html')) 
        
        
# This method processes the data POSTed by the login form; to display the form itself, call /login/form
# Furnish your mail id and password and get a token
@app.route('/login', methods =['GET', 'POST']) 
@app.route('/signin', methods =['GET', 'POST']) 
def login(): 
    if request.method == 'GET':
        return ({'success' : False, 'msg' : 'Please POST the email and password'})
    # takes either an HTML form, or json object in the HTTP POST payload 
    if (request.json):
        form = request.json   
    else:
        form = request.form 
    dprint ('Login form: ', form)
    if not form : 
        return ({'success' : False, 'msg' : 'Login required'}, 401)   
    mail = form.get('email')
    passwd = form.get('password')  
    if mail is None or passwd is None : 
        return ({'success' : False, 'msg' : 'Missing email or password'}, 401) 
    intof_id = user_reg.email_intof_map (mail)     
    if (intof_id is None):
        return ({'success' : False, 'msg' : 'Invalid user'}, 401)
    session['current_user'] = intof_id  # test this well: sometimes the session leaked across two browsers
    msg = 'User {} logged in.'.format(intof_id)
    dprint (msg)
    return {'success' : True, 'msg' : msg}
    
            
# This is a quick and dirty new user registration form, in case there is no real client that can POST a form
@app.route('/registration/form')
def user_registration_form():    
    return (render_template('register.html'))        
    
    
# this method processes the registration form after it is posted
@app.route('/register', methods =['GET','POST']) 
def signup(): 
    if request.method == 'GET':
        return ({'success' : False, 'msg' : 'Please POST the email, user name and password in a form'})
    # make a dictionary out of POSTed data 
    if (request.json):
        form = request.json    
    else:
        form = request.form 
    if (not form):
        return ({'success' : False, 'msg' : 'email, name and password are required'}) 
    name, email = form.get('name'), form.get('email') 
    print (name, email)
    password = form.get('password') 
    if (not name or not email or not password):
        return ({'success' : False, 'msg' : 'Please fill in email, name and password'}) 
    if (len(name)==0 or len(email)==0 or len(password)==0):
        return ({'success' : False, 'msg' : 'email, name or password cannot be blank'})    
    if ('@' not in email or '.' not in email):
        return ({'success' : False, 'msg' : 'invalid email'})       
    user =  dict(email=email, name=name, passhash=user_reg.create_password_hash (password))  
    return (user_reg.create_user (user))


# This is a quick and dirty device config form, in case there is no real client that can POST a form
@app.route('/device/config/form')
def device_config_form():    
    iid = session.get ('current_user')  
    if iid is None:
        return {'success' : False, 'ERROR' : 'User must be logged in to see the devices'}
    dev_list = device_map.get_user_devices(iid)  # to popuoate the drop down device list on the page
    print ('Your devices: ', dev_list)
    if (dev_list is None or len(dev_list)==0):
        return {'success' : False, 'ERROR' : 'User has no registered devices'}
    return (render_template('device.html', ServerVar=dev_list))   # this page will inject intof_id 


# this method processes the device confiuration form after it is posted
@app.route('/config/device', methods =['GET','POST']) 
def configure_device(): 
    if request.method == 'GET':
        return ({'success' : False, 'msg' : 'Please POST the device names in a form'})
    iid = session.get ('current_user')  
    dprint ('current user: ', iid)
    if  iid is None:
        print ('ERROR: User must be logged in before adding a device.')   
        return (render_template('login.html')) # TODO: what if they are using their own login page?
    # make a dictionary out of POSTed data 
    if (request.json):
        form = request.json    
    else:
        form = request.form 
    if (not form):
        return ({'success' : False, 'msg' : 'Device names are required'}) 
    print (form)
    room = form.get('room_name')
    print ('Room Name (ignored!): ', room) # TODO: client should save this in its micro DB
    devid = form.get('device_id')
    if  devid is None:
        return ({'success' : False, 'msg' : 'Device names are required'}) 
    print ('Configuring device for user: ', iid)
    # TODO: make this flexible: from 1 to 8 relays are possible; also handle sensors
    device = { 
        'intof_id' : iid,
        'device_id' : devid,
        'relsens' : {
            'POWER1' : form.get('POWER1', 'switch one'), 
            'POWER2' : form.get('POWER2', 'switch two'), 
            'POWER3' : form.get('POWER3', 'switch three'), 
            'POWER4' : form.get('POWER4', 'switch four')
        } # Tasmota expects POWER1, POWER2 etc as relay names; do not change these!
    }                    
    return (device_reg.upsert_device (device))
    
    