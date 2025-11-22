import pymysql

db_config = {
    'host':'localhost',
    'user':'root',
    'password':'root',  
    'cursorclass' : pymysql.cursors.DictCursor,
    'database': 'NOTESMANAGER_26'
}

def get_connection():    
    conn = pymysql.connect(**db_config)
    return conn

def db_init():    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS USERS
        (
            USERID INT PRIMARY KEY AUTO_INCREMENT,
            USERNAME VARCHAR(30) NOT NULL,
            USERMAIL VARCHAR(50) NOT NULL UNIQUE,
            USERPASSWORD VARCHAR(10) NOT NULL
        )
        '''        
    )  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USEROTP
        (
            USERNAME VARCHAR(30) NOT NULL,
            USERMAIL VARCHAR(50) NOT NULL UNIQUE,
            USERPASSWORD VARCHAR(10) NOT NULL,
            OTP INT NOT NULL
        )'''
    )
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NOTES
        (USERID INT NOT NULL,
        NOTESID INT PRIMARY KEY AUTO_INCREMENT,
        TITLE VARCHAR(100) NOT NULL,
        CONTENT VARCHAR(250) NOT NULL
        ) '''

    )
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS FILES
            (FID INT AUTO_INCREMENT PRIMARY KEY,
            FILENAME VARCHAR(30) NOT NULL,
            FILEPATH VARCHAR(50) NOT NULL,
            USERID INT NOT NULL
            )'''
        )
    cursor.close()
    conn.close()
    
def registered_user(email):   
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM USERS
        WHERE USERMAIL = %s
        ''', (email,)
    )
    user = cursor.fetchone() #tuple, None
    return user


def insert_userotp(uname, umail,upassword, uotp ):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                 INSERT INTO USEROTP
                 VALUES
                 (%s,%s,%s,%s)  
                   ''', (uname, umail, upassword, uotp))
    conn.commit()
    cursor.close()
    conn.close()
    
def check_userotp(email):   
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM USEROTP
        WHERE USERMAIL = %s
        ''', (email,)
    )
    user = cursor.fetchone() #tuple, None
    return user

def insert_users(uname, umail,upassword ):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                 INSERT INTO USERS
                 (USERNAME, USERMAIL, USERPASSWORD )
                 VALUES
                 (%s,%s,%s)  
                   ''', (uname, umail, upassword))
    conn.commit()
    cursor.close()
    conn.close()  
    
def check_userpassword(mail, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM USERS
        WHERE USERMAIL = %s AND USERPASSWORD = %s
        ''',(mail, password)
    )
    user_exist = cursor.fetchone()
    cursor.close()
    conn.close()
    return user_exist
def add_notes(userid, title, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO NOTES
        (USERID, TITLE, CONTENT)
        VALUES
        (%s, %s, %s)
        ''', (userid, title, content)
    )
    conn.commit()
    cursor.close()
    conn.close()
def display_notes(userid):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM NOTES
        WHERE USERID=%s
        ''',(userid,)
)
    user_notes=cursor.fetchall()
    
    cursor.close()
    conn.close()
    return user_notes
def get_note(nid):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM NOTES
        WHERE NOTESID=%s
        ''',(nid,)
    )
    note=cursor.fetchone()
    cursor.close()
    conn.close()
    return note
def update_notes(nid, title, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE NOTES
        SET TITLE=%s, CONTENT=%s
        WHERE NOTESID=%s
        ''', (title, content, nid)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_notes(nid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        DELETE FROM NOTES
        WHERE NOTESID=%s
        ''', nid
    )
    conn.commit()
    cursor.close()
    conn.close()
def db_add_file(filename,fpath,userid):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        INSERT INTO FILES
        (FILENAME, FILEPATH, USERID)
        VALUES(%s,%s,%s)
        ''',(filename,fpath,userid)
    )
    conn.commit()
    cursor.close()
    conn.close()
def db_get_files(userid):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM FILES
        WHERE USERID=%s
        ''',userid
    )
    files=cursor.fetchall()
    cursor.close()
    conn.close()
    return files

def db_get_file(fid):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM FILES
        WHERE FID=%s
        ''',fid
    )
    file=cursor.fetchone()
    cursor.close()
    conn.close()
    return file
def db_delete_file(fid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        DELETE FROM FILES
        WHERE FID=%s
        ''', fid
    )
    conn.commit()
    cursor.close()
    conn.close()
def db_search(query_par):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM NOTES
        WHERE CONTENT LIKE %s
        ''',f'%{query_par}%' 
    )
    notes=cursor.fetchall()
    cursor.close()
    conn.close()
    return notes
def db_password_reset(email,new):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute(
        '''
        UPDATE USERS
        SET USERPASSWORD=%s
        WHERE USERMAIL=%s
        ''',(new,email)
    )
    conn.commit()
    cursor.close()
    conn.close()
