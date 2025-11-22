from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
from database import (db_init, registered_user, insert_userotp,check_userotp,insert_users, check_userpassword, add_notes, display_notes, get_note, update_notes, delete_notes, db_add_file, db_get_files, db_get_file, db_delete_file, db_search, db_password_reset)
import smtplib
from email.message import EmailMessage
import random
import os
from itsdangerous import URLSafeTimedSerializer
app = Flask(__name__)
app.secret_key='Notes Manager App'
serializer=URLSafeTimedSerializer(app.secret_key)

db_init()

admin_email = 'vijayagirisravanthi0724@gmail.com'
admin_password = 'mjuj jhep qhql mrtv'

def send_mail(to_email, body):    
    msg = EmailMessage()
    msg.set_content(body)
    msg['To'] = to_email
    msg['From'] = admin_email
    msg['Subject'] = 'OTP verification'
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(admin_email, admin_password)
        smtp.send_message(msg)

@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')        
        
        if registered_user(email):
            return redirect(url_for('login'))
        
        if check_userotp(email):
            return redirect(url_for('verify_otp', email = email ))
        
        otp = random.randint(100000, 999999)
        body = f'''Please enter this OTP for verification.
                 Do not share this OTP with anyone.
                 OTP - {otp}'''
                 
        send_mail(email, body)
        insert_userotp(username, email, password, otp)
        
        #return redirect(url_for('verify_otp', email = email))
        return render_template('verify_otp.html', email = email)
    
    return render_template('register.html')

@app.route('/verify_otp/<email>', methods = ['POST', "GET"])
def verify_otp(email):
    if request.method == 'POST':
        otp = int(request.form.get('otp'))
        user_dict = check_userotp(email)
        db_otp = user_dict['OTP']
        if otp != db_otp:
            msg = "Invalid OTP"
            msg_type = "error"
            return render_template('verify_otp.html', message = msg, message_type = msg_type, email = email)
        else:
            user_details = check_userotp(email)
            username = user_details['USERNAME']
            password = user_details['USERPASSWORD']
            insert_users(username, email, password)
            msg = "Registered Successfully"
            msg_type = "success"
            return render_template('login.html')       
    return render_template('verify_otp.html', email = email)
    
@app.route('/login',methods = ['POST', "GET"])
def login():
    if request.method == 'POST':
       

        mail = request.form.get('usermail')
        password = request.form.get('password')
        user = check_userpassword(mail, password)
        username=user['USERNAME']
        userid=user['USERID']
        if user:
            session['username']=username
            session['user_id']=userid
            return render_template('dashboard.html')
        else:
            msg = "Invalid credentials"
            msg_type = "error"
            return render_template('login.html', message = msg, message_type = msg_type)
    
    return render_template('login.html')

@app.route('/forgot_password',methods=['POST','GET'])
def forgot_password():
    if request.method=='POST':
        email=request.form.get('email')
        if not registered_user(email):
            msg='No User Registered'
            msg_type='error'
            return render_template('register.html', message=msg, message_type=msg_type)
        
        token= serializer.dumps(email,salt='password-reset')
        reset_url=url_for('reset_password',token=token, _external=True)
        body=f'Follow this link for resetting password:{reset_url}'
        send_mail(email,body)
    return render_template('forgot_password.html')
@app.route('/reset_password/<token>',methods=['POST','GET'])
def reset_password(token):
    email=serializer.loads(token,salt='password-reset')
    if request.method=='POST':
        password=request.form.get('password')
        db_password_reset(email,password)
        msg='Password reset successful'
        msg_type='success'
        return render_template('login.html', message=msg, message_type=msg_type)    
    return render_template('reset_password.html', token=token)
@app.route('/dashboard')
def dashboard():
    if session:
        return render_template('dashboard.html')
    message='No user logged in'
    message_type='error'
    return render_template('login.html', message=message, message_type=message_type)
    
@app.route('/add_note', methods = ['POST', 'GET'])
def add_note():
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message = msg, message_type = msg_type)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        userid = session['user_id']
        add_notes(userid, title, content)
        msg = 'Notes Added Successfully'
        msg_type = 'success'
        return render_template('add_note.html', message = msg, message_type = msg_type)

    return render_template('add_note.html')
@app.route('/view_notes')
def view_notes():
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    userid=session['user_id']
    notes=display_notes(userid)

    return render_template('view_notes.html',notes=notes)
@app.route('/view_note/<int:nid>')
def view_note(nid):
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    note=get_note(nid)
    return render_template('view_note.html', note=note)

@app.route('/update_note/<int:nid>', methods=['POST', 'GET'])
def update_note(nid):
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    note = get_note(nid)  
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        update_notes(nid, title, content)
        
        return redirect(url_for('view_notes'))
    return render_template('update_note.html', note=note)

@app.route('/delete_note/<int:nid>')
def delete_note(nid):
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    delete_notes(nid)
    return redirect(url_for('view_notes'))
    
@app.route('/upload_file',methods=['POST','GET'])
def upload_file():
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    if request.method=='POST':
        file=request.files.get('file')
        filename=file.filename
        filepath=os.path.join('uploads',filename)
        file.save(filepath)
        userid=session['user_id']
        db_add_file(filename,filepath,userid)
        msg='File uploaded successfully'
        msg_type='success'
        return render_template('upload_file.html',message=msg,message_type=msg_type)
    return render_template('upload_file.html')
@app.route('/view_files')
def view_files():
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    userid=session['user_id']
    files=db_get_files(userid)
    return render_template('view_files.html',files=files)


@app.route('/view_file/<int:fid>')
def view_file(fid):
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    file=db_get_file(fid)
    file_path=file['FILEPATH']
    return send_file(file_path, as_attachment=False)
@app.route('/download_file/<int:fid>')
def download_file(fid):
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    file=db_get_file(fid)
    file_path=file['FILEPATH']
    return send_file(file_path, as_attachment=True)
    
@app.route('/delete_file/<int:fid>')
def delete_file(fid):
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    file=db_get_file(fid)
    file_path=file['FILEPATH']
    os.remove(file_path)
    db_delete_file(fid)
    return redirect(url_for('view_files'))
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session:
        message = 'No user logged in'
        message_type = 'error'
        return render_template('login.html', message=message, message_type=message_type)
    if request.method=='POST':
        query_par=request.form.get('query')
        notes=db_search(query_par)
        return render_template('search.html',notes=notes)
    return render_template('search.html')

@app.route('/export_notes')
def export_notes():
    userid=session['user_id']
    user_notes=display_notes(userid)
    text=''
    for note in user_notes:
        text+=note['TITLE']+'\n'
        text+=note['CONTENT']+'\n'
        text+='\n'
    return Response(text,mimetype='text/plain',headers={'content-disposition':'attachable'})
@app.route('/logout')
def logout():
    if session:
        session.pop('username')
        session.pop('user_id')
        msg='logged out successfully'
        msg_type='success'
        return render_template('login.html', message=msg, message_type=msg_type)
    msg='No user logged in'
    msg_type='error'
    return render_template('login.html', message=msg, message_type=msg_type)

app.run(debug = True, port = 5002)