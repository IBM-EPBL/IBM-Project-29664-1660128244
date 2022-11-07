from flask import Flask,redirect,url_for,render_template,request,make_response
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=db2.crt;UID=bxr06206;PWD=gEMlHs5QLV6LyGB0",'','')
print(conn)
print("connection successful...")
app = Flask(__name__)




@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        sql = "select * from user where username=? and password=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        dic = ibm_db.fetch_assoc(stmt)
        print(dic)
        if dic:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
        return redirect(url_for('home'))
    elif request.method=='GET':
        return render_template('login.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        roll_no = request.form['roll_no']
        sql = "insert into user values(?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(prep_stmt,1,email)
        ibm_db.bind_param(prep_stmt,2,username)
        ibm_db.bind_param(prep_stmt,3,roll_no)
        ibm_db.bind_param(prep_stmt,4,password)
        ibm_db.execute(prep_stmt)
        #db post operation
        return redirect(url_for('login'))
    elif request.method=='GET':
        return render_template('signup.html')


if __name__=='__main__':
    app.run(debug = True)