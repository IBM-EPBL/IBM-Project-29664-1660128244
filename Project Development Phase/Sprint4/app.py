from http import client
from flask import Flask, render_template, redirect, url_for, request, session, flash, Markup
import ibm_db
import sendgrid #Email API
import os
import json, re
from dotenv import load_dotenv  #API that exposes environmental variables into the program
from sendgrid.helpers.mail import Mail, Email, To, Content  #Additional Email Helper Classes

app = Flask(__name__)

load_dotenv()   #load keys from .env

#secret key required to maintain unique user sessions
app.secret_key = os.environ.get('APP_KEY')

#establish connection with IBM Db2 Database
connection = ibm_db.connect("DATABASE=bludb;HOSTNAME=815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30367;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=fzx82079;PWD=Gemfhl3b2DRTeUqB;", "", "")

#Email Prerequisites
sg = sendgrid.SendGridAPIClient(api_key = os.environ.get('SENDGRID_API_KEY'))   #set SendGrid API Key
from_email = Email("getplasmaproject@gmail.com")     #the address that sends emails to the users

#WhatsApp Prerequisites
account = os.environ.get('TWILIO_ACCOUNT_SID')
token = os.environ.get('TWILIO_AUTH_TOKEN')
sender_phone = os.environ.get('TWILIO_WHATSAPP')   #the number from which messages are sent to the user


bucket_name = 'getplasma-pvt'



@app.route('/')
@app.route('/dashboard')
def dashboard():
    if not session:
        return redirect(url_for('signin'))  #ask user to sign in if not done already

    return render_template('dashboard.html')  #go to homepage if signed in




@app.route('/signout')
def signout():
    session.clear()   #remove user session upon signing out
    return redirect('/')




@app.route('/register')
def register():
    if 'UID' in session:   #inform user if they're already signed in the same session
        flash('You are already logged in! Sign out to login with a different account')
        return redirect(url_for('dashboard'))

    else:
        return render_template('register.html') #take user to the registration page




@app.route('/regform', methods=['POST'])
def regform():
    #get user details from the registration form
    uname = request.form['uname']
    utype = request.form['utype']   #Select email or phone number
    uid = request.form['uid']       #Selected contact id type
    pwd = request.form['pwd']
    dtype = request.form['dtype']   #donor/patient user type

    sql = 'SELECT * from ' + dtype + ' WHERE uid=?'   #check if user is already registered
    pstmt = ibm_db.prepare(connection, sql)
    ibm_db.bind_param(pstmt, 1, uid)
    ibm_db.execute(pstmt)

    acc = ibm_db.fetch_assoc(pstmt)

    if acc:     #inform user to sign in if they have an existing account
        flash('You are already a registered member. Please sign in using your registered credentials')

    else:
        sql = 'INSERT INTO ' + dtype + ' (uid, pwd, uname) VALUES(?,?,?)' #insert credentials of new user to the database
        pstmt = ibm_db.prepare(connection, sql)
        ibm_db.bind_param(pstmt, 1, uid)
        ibm_db.bind_param(pstmt, 2, pwd)
        ibm_db.bind_param(pstmt, 3, uname)
        ibm_db.execute(pstmt)

        if utype == 'mail':

            to_email = To(uid)   #set user as recipient for confirmation email
            subject = "Welcome to GetPlasma"
            content = Content("text/html", "<p>Hello " + uname + ",</p><p>Thank you for registering to the GetPlasma Application!</p><p>If this wasn't you, then immediately report to our <a href=\"mailto:getplasmaproject@gmail.com\">admin</a> or just reply to this email.</p>")

            email = Mail(from_email, to_email, subject, content) #construct email format
            email_json = email.get()    #get JSON-ready representation of the mail object

            response = sg.client.mail.send.post(request_body = email_json)  #send email by invoking an HTTP/POST request to /mail/send
        
        else:   #if user registered with phone number
            
            flash(
                Markup(
                    '''<div class="d-flex flex-column">
                            <div class="d-flex flex-row align-items-center mb-3">
                                <div class="text-start me-3">Please join our WhatsApp Chat to receive alerts by clicking the button below or just scan the QR Code</div>
                                <img class="rounded" width="50%" src="https://plasma-donor.s3.jp-tok.cloud-object-storage.appdomain.cloud/WhatsAppQR.png"/>
                            </div>
                            <a class="btn btn-light btn-sm" target="_blank" href="https://wa.me/14155238886?text=join%20did-take">Join</a>
                        </div>'''
                )
            )
        
        flash('Registration Successful! Sign in using the registered credentials to continue')


    return redirect(url_for('signin'))  #ask users to sign in after registration




@app.route('/signin')
def signin():
    if 'UID' in session:   #inform user if they're already signed in the same session
        flash('You are already signed in! Sign out to login with a different account')
        return redirect(url_for('dashboard'))
    return render_template('signin.html')   #take user to the sign in page




@app.route('/signinform', methods=['POST'])
def signinform():
    uid = request.form['uid']   #get user id and password from the form
    pwd = request.form['pwd']
    dtype = request.form['dtype']

    sql = 'SELECT * from ' + dtype + ' WHERE uid=? AND pwd=?' #check user credentials in the database
    pstmt = ibm_db.prepare(connection, sql)
    ibm_db.bind_param(pstmt, 1, uid)
    ibm_db.bind_param(pstmt, 2, pwd)
    ibm_db.execute(pstmt)

    acc = ibm_db.fetch_assoc(pstmt)
    
    if acc: #if the user is already registered to the application
        for keys, vals in acc.items():
            session[keys] = vals
        session['DTYPE'] = dtype
        session['UTYPE'] = request.form['utype'] #Email/Phone Number
        flash('Signed in successfully!')
        return redirect(url_for('dashboard'))
        
    else:   #warn upon entering incorrect credentials
        flash('Incorrect credentials. Please try again!')
        return render_template('signin.html')


@app.route('/medform', methods=['POST'])
def medform():
    #get user details from the registration form
    uname = request.form['uname']
    uid = request.form['uid']       #Selected contact id type
    uage = request.form['uage']
    gender = request.form['gender']
    weight = request.form['weight']
    bgroup = request.form['bgroup']
    rh = request.form['rh']
    dtype = session['DTYPE']  #donor/patient user type
    if dtype == 'Donor':
        medfile = request.files['medfile']
    addr = request.form['addr']
    city = request.form['city']
    st = request.form['st']
    zip = request.form['zip']



    




    

    sql = 'SELECT * from ' + dtype + ' WHERE uid=?'
    pstmt = ibm_db.prepare(connection, sql)
    ibm_db.bind_param(pstmt, 1, uid)
    ibm_db.execute(pstmt)

    res = ibm_db.fetch_assoc(pstmt)

    if res:
        flash('Profile updated successfully')
        for keys, vals in res.items():
            session[keys] = vals
    else:
        flash('Error occured while trying to update the profile')

    return redirect(url_for('dashboard'))


@app.route('/donors')
def donors():
    sql = 'SELECT uid, uname, uage, gender, weight, bgroup, rh, medfile, addr, city, st, zip from DONOR'
    stmt = ibm_db.exec_immediate(connection, sql)
    
    donor_list = {}
    i=0
    while (res:=ibm_db.fetch_assoc(stmt)) != False:
        donor_list[i] = res
        i+=1

    return render_template('donors.html', donors = donor_list)



@app.route('/processRequestPlasma/<string:userinfo>', methods=['POST'])     #alert donors upon request
def processRequestPlasma(userinfo):
    donor_det = json.loads(userinfo)
    if re.fullmatch('[0-9]{10}', donor_det['uid']): #if donor is registered with phone number
        message = client.messages.create(
                from_='whatsapp:'+sender_phone,
                body= f'''Hello, {donor_det['uname']}
\nOne of our users need your help now! Mx.{session['UNAME']} has requested you to donate your plasma to them. We've hereby provided their medical and contact details for your reference.\n\n
Name         : {session['UNAME']}\n
Age          : {session['UAGE']}\n
Gender       : {session['GENDER']}\n
Blood Group  : {session['BGROUP'] + session['RH']}\n
Weight       : {session['WEIGHT']} kg\n
Address :\n
{session['ADDR']}\n{session['CITY']}\n{session['ST']} - {session['ZIP']}
You can contact them here: {session['UID']}\n\n
Hope you use this opportunity to save someone's life.\n\n
Regards,\nTeam GetPlasma''',
        to='whatsapp:+91'+donor_det['uid']
)
    
    
    else:   #if donor is registered with email
        to_email = To(donor_det['uid'])   #set recipient as the selected donor
        subject = "IMPORTANT - Plasma Required"
        #send the details of the requested patient to 
        content = Content(
                    "text/html", 
                    f'''<p>Hello, {donor_det['uname']}</p>
                        <p>One of our users need your help now!</p>
                        <p>Mx.{session['UNAME']} has requested you to donate your plasma to them. We've hereby provided their medical and contact details for your reference.<p> 
                        <p>Name         : {session['UNAME']}</p>
                        <p>Age          : {session['UAGE']}</p>
                        <p>Gender       : {session['GENDER']}</p>
                        <p>Blood Group  : {session['BGROUP'] + session['RH']}</p>
                        <p>Weight       : {session['WEIGHT']} kg</p>
                        <p>Address : </p>
                        <p>{session['ADDR']} <br> {session['CITY']} <br> {session['ST']} - {session['ZIP']}</p>
                        <br><br><br>
                        <p>Click <a href=\"{'mailto:' if session['UTYPE'] == 'email' else 'tel:+91'}{session['UID']}\">here</a> to contact them</p>
                        <br><br>
                        <p>Hope you use this opportunity to save someone's life</p>
                        <br><br>
                        <p>Regards,<br>Team GetPlasma</p>''')
        

        email = Mail(from_email, to_email, subject, content) #construct email format
        email_json = email.get()    #get JSON-ready representation of the mail object

        response = sg.client.mail.send.post(request_body = email_json)  #send email by invoking an HTTP/POST request to /mail/send

    return('/')