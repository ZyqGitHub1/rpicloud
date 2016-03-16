#!/usr/bin/env python
# -*- coding: utf-8 -*-
# RPIcould
# A microcloudmannager for raspberry application written with Flask and sqlite3.

# import all
import chartkick
import os
import time
import sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, Response, jsonify
from werkzeug import check_password_hash, generate_password_hash
from contextlib import closing
from send_email import send_email
#import RPi.GPIO as GPIO
#import mygpio
# emulated camera
from camera import Camera
# Raspberry Pi camera module (requires picamera package)
#from camera_pi import Camera
# configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir,"db","user.db")

DATABASE = db_path
#PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.jinja_env.add_extension("chartkick.ext.charts")  
# find configuration from this .py
app.config.from_object(__name__)

#数据库连接函数
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

#数据库创建函数
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("schema.sql",mode = "r") as f:
            db.cursor().executescript(f.read())
        db.commit()

#数据库操作
#请求之后关闭数据库
@app.teardown_appcontext
def close_database(exception):
    #Closes the database again at the end of the request.
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()
#请求之前打开数据库，并查询user_id，返回user的所有信息
@app.before_request
def before_request():
    g.db = connect_db()
#数据库查询函数
def query_db(query, args=(), one=False):
    #Queries the database and returns a list of dictionaries.
    cur = connect_db().execute(query, args)
    #return the select info
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv
#通过username获取user_id
def get_user_id(username):
    #Convenience method to look up the id for a username.
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None
#通过lightname获取light_id
def get_light_id(light):
    rv = query_db('select pin_id from light where light_name = ?',
                  [light], one=True)
    return rv[0] if rv else None
#通过email获取email_id
def get_email_id(email):
    #Convenience method to look up the id for a username.
    rv = query_db('select email_id from email where email = ?',
                  [email], one=True)
    return rv[0] if rv else None
#获取用户头像
def gravatar_url(email, size=80):
    #Return the gravatar image for the given email address.
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

# 获取收发信email信息
#from_email = query_db("SELECT email,email_pw FROM email WHERE access = 0")
#to_email = query_db("SELECT email FROM email WHERE access = 1")

# 11端口上沿电压回调函数
#def rising_activation_callback(channel):
#    cur = g.db.execute('SELECT light_name, mode FROM light ORDER BY pin_id DESC')
#    l_list = cur.fetchall()
#    cur = g.db.execute('SELECT config_status FROM config ORDER BY config_id DESC')
#    config_status = cur.fetchall()
#    from_email = query_db("SELECT email,email_pw FROM email WHERE access = 0")
#    to_email = query_db("SELECT email FROM email WHERE access = 1")
#    for row in l_list:
#        if row[1] == "2":
#            gpio_out_on(int(row[0]))
#        elif row[1] == "3":
#            if config_status[1][0] == "1":
#                gpio_out_on(int(row[0]))
#    if config_status[2][0] == "1":
#        send_email(from_email[0][0],from_email[0][1],to_email[0],smtp_server = "smtp.qq.com")
#    elif config_status[2][0] == "2":
#        if config_status[1][0] == "1":
#            send_email(from_email[0][0],from_email[0][1],to_email[0],smtp_server = "smtp.qq.com")
#    g.db.close()
## 11端口下沿电压回调函数
#def falling_activation_callback(channel):
#    cur = g.db.execute('SELECT light_name, mode FROM light ORDER BY pin_id DESC')
#    l_list = cur.fetchall()
#    cur = g.db.execute('SELECT config_status FROM config ORDER BY config_id DESC')
#    config_status = cur.fetchall()
#    from_email = query_db("SELECT email,email_pw FROM email WHERE access = 0")
#    to_email = query_db("SELECT email FROM email WHERE access = 1")
#    for row in l_list:
#        if row[1] == "2":
#            gpio_out_off(int(row[0]))
#        elif row[1] == "3":
#            if config_status[1][0] == "1":
#                gpio_out_off(int(row[0]))
#    if config_status[2][0] == "1":
#        send_email(from_email[0][0],from_email[0][1],to_email[0],smtp_server = "smtp.qq.com")
#    elif config_status[2][0] == "2":
#        if config_status[1][0] == "1":
#            send_email(from_email[0][0],from_email[0][1],to_email[0],smtp_server = "smtp.qq.com")
#    g.db.close()
## 13端口上沿电压回调函数
#def rising_dark_callback(channel):
#    cur = g.db.execute('SELECT light_name, mode FROM light ORDER BY pin_id DESC')
#    l_list = cur.fetchall()
#    cur = g.db.execute('SELECT config_status FROM config ORDER BY config_id DESC')
#    config_status = cur.fetchall()
#    for row in l_list:
#        if row[1] = "1":
#            gpio_out_on(int(row[0]))
#    g.db.execute('UPDATE config SET config_status = "1" WHERE config_name = "dark"')
#    g.db.commit()
#    g.db.close()
## 13端口下沿电压回调函数
#def falling_dark_callback(channel):
#    cur = g.db.execute('SELECT light_name, mode FROM light ORDER BY pin_id DESC')
#    l_list = cur.fetchall()
#    cur = g.db.execute('SELECT config_status FROM config ORDER BY config_id DESC')
#    config_status = cur.fetchall()
#    for row in l_list:
#        if row[1] = "1":
#            gpio_out_off(int(row[0]))
#    g.db.execute('UPDATE config SET config_status = "0" WHERE config_name = "dark"')
#    g.db.commit()
#    g.db.close()
## 端口模式设置
#GPIO.setmode(GPIO.BOARD)
## 设置下拉电位
#GPIO.setup(11,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
#GPIO.setup(13,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
## 11端口上沿电压中断检测
#GPIO.add_event_detect(11,GPIO.RISING,callback = rising_activation_callback,bouncetime = 200)
## 11端口下沿电压中断检测
#GPIO.add_event_detect(11,GPIO.FALLING,callback = falling_activation_callback,bouncetime = 200)
## 13端口上沿电压中断检测
#GPIO.add_event_detect(13,GPIO.RISING,callback = rising_callback,bouncetime = 200)
## 13端口下沿电压中断检测
#GPIO.add_event_detect(13,GPIO.FALLING,callback = falling_callback,bouncetime = 200)
@app.route("/",methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = query_db("select * from user where username = ?", [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user[3],request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user[0]
            session['logged_in'] = True
            session['username'] = user[1]
            return redirect(url_for("welcome"))
    return render_template('login.html', error=error)

@app.route("/welcome/")
def welcome():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("welcome.html")

@app.route("/switch/")
def switch():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("switch.html")

@app.route("/register/",methods=['GET', 'POST'])
def register():
    error = None
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = connect_db()
            db.execute("INSERT INTO user (username, email, pw_hash,access) VALUES (?, ?, ?, ?)",
              [request.form['username'], request.form['email'],
               generate_password_hash(request.form['password']),request.form['access']])
            db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/gpio/',methods=['POST'])
def gpio():
    if request.method == 'POST':
        id = int(request.form['id'])
        GPIO.setmode(GPIO.BOARD)
        if request.form['turn'] == "on":
            GPIO.setup(id,GPIO.OUT)
            GPIO.output(id,True)
        if request.form['turn'] == "off":
            GPIO.setup(id,GPIO.OUT)
            GPIO.output(id,False)
    return redirect(url_for('switch'))

@app.route("/logout/")
def logout():
    session.pop("logged_in",None)
    session.pop("user_id",None)
    session.pop("username",None)
    flash("You were logged out")
    return redirect(url_for("login"))

@app.route("/changeadmin/",methods=['GET', 'POST'])
def change_admin_password():
    error = None
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        password = query_db("SELECT * FROM user WHERE username = ?", ["admin"], one=True)
        if not check_password_hash(password[3],request.form['admin_password']):
            error = 'Invalid password'
        elif not request.form['admin_newpassword1']:
            error = 'You have to enter a password'
        elif request.form['admin_newpassword1'] != request.form['admin_newpassword2']:
            error = 'The two passwords do not match'
        else:
            g.db.execute("UPDATE user SET pw_hash = ? WHERE username = 'admin'",
              [generate_password_hash(request.form['admin_newpassword1'])])
            db.commit()
            flash('You were successfully change and can login now')
            return redirect(url_for('logout'))
    return render_template('change_admin_password.html', error=error)

@app.route("/email/",methods=['GET', 'POST'])
def email():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    cur = g.db.execute('select email, access from email order by email_id desc')
    emaillist = [dict(email=row[0], access=row[1]) for row in cur.fetchall()]
    if request.method == 'POST':
        if request.form['access'] == "0":
            return render_template('email0.html') 
        if request.form['access'] == "1":
            return render_template('email1.html')
    return render_template('chooseemail.html',emaillist = emaillist)

@app.route("/emailsend/",methods=['GET', 'POST'])
def emailsend():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    error = None
    if request.method == 'POST':
        if not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['email_pw1']:
            error = 'You have to enter a password'
        elif request.form['email_pw1'] != request.form['email_pw2']:
            error = 'The two passwords do not match'
        elif get_email_id(request.form['email']) is not None:
            error = 'The username is already taken'
        else:
            db = connect_db()
            db.execute("insert into email (email, email_pw, access) values (?, ?, 0)",
              [request.form['email'], request.form['email_pw1']])
            db.commit()
            flash('You were successfully registered and can login now')
        if error != None:
            return render_template('email0.html',error = error)
        else:
            return redirect(url_for("email"))

@app.route("/emailrec/",methods=['GET', 'POST'])
def emailrec():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    error = None
    if request.method == 'POST':
        if not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif get_email_id(request.form['email']) is not None:
            error = 'The username is already taken'
        else:
            db = connect_db()
            db.execute("insert into email (email , access) values (?, 1)",
              [request.form['email']])
            db.commit()
            flash('You were successfully registered and can login now')
        if error != None:
            return render_template('email1.html',error = error)
        else:
            return redirect(url_for("email"))

@app.route("/manage/",methods=['GET', 'POST'])
def manage():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    emailcur = g.db.execute('select email, access from email order by email_id desc')
    emaillist = [dict(email=row[0], access=row[1]) for row in emailcur.fetchall()]
    usercur = g.db.execute('select username, access from user where user_id > 1 order by user_id desc')
    userlist = [dict(username=row[0], access=row[1]) for row in usercur.fetchall()]
    return render_template('manage.html',emaillist = emaillist,userlist = userlist)

@app.route("/manage/user/",methods=['GET', 'POST'])
def manage_user():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    error = None
    if request.method == 'POST':
        if request.form.getlist("deleteuser") == None:
            error = 'No select'
        else:
            deleteuser = request.form.getlist("deleteuser")
            db = connect_db()
            for deletusername in deleteuser:
                db.execute("DELETE FROM user WHERE username = ?",[deletusername])
            db.commit()
    return redirect(url_for("manage"))
@app.route("/manage/email/",methods=['GET', 'POST'])
def manage_email():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    error = None
    if request.method == 'POST':
        if request.form.getlist("deleteemail") == None:
            error = 'No select'
        else:
            deleteemaillist = request.form.getlist("deleteemail")
            db = connect_db()
            for deleteemail in deleteemaillist:
                db.execute("DELETE FROM email WHERE email = ?",[deleteemail])
            db.commit()  
        return redirect(url_for("manage"))

@app.route("/config/",methods=['GET', 'POST'])
def config():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    #status = query_db("SELECT config_status FROM config WHERE config_name = 'email_status'")
    #email_status = status[0][0]
    error = None
    cur = g.db.execute('SELECT light_name, mode FROM light ORDER BY pin_id DESC')
    lightlist = [dict(name = row[0], mode = row[1]) for row in cur.fetchall()]
    if request.method == 'POST':
        if not request.form["email_s"]:
            error = "no mode"
        else:
            g.db.execute("UPDATE config SET config_status = ? WHERE config_name = 'email_status'",
              [request.form["email_s"]])
            g.db.commit()
        for row in lightlist:
            if not request.form[row["name"]]:
               error = "no lightmode"
            else: 
                g.db.execute("UPDATE light SET mode = ? WHERE light_name = ?",
              [request.form[row["name"]],row["name"]])
                g.db.commit()
        if not request.form.getlist("deletelight"):
            error = "no delete"
        else:
            deletelight = request.form.getlist("deletelight")
            for deletelightname in deletelight:
               g.db.execute("DELETE FROM light WHERE light_name = ?",[deletelightname])
            g.db.commit()
    status = query_db("SELECT config_status FROM config WHERE config_name = 'email_status'")
    email_status = status[0][0]
    cur = g.db.execute('SELECT light_name, mode FROM light ORDER BY pin_id DESC')
    lightlist = [dict(name = row[0], mode = row[1]) for row in cur.fetchall()]
    return render_template('config.html',lightlist = lightlist,error = error,email_status = email_status)
        
@app.route("/config/add/",methods=['GET', 'POST'])
def config_add():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        if not request.form["newlight"]:
            error = "没有输入要添加的端口号"
        elif get_light_id(request.form['newlight']) is not None:
            error = "端口已存在"
        else:
            g.db.execute("INSERT INTO light (light_name , mode) VALUES (?, '0')",
              [request.form['newlight']])
            g.db.commit()
    return redirect(url_for("config"))



@app.route('/camera/')
def camera():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    """Video streaming home page."""
    return render_template('cam.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/temp/",methods=['GET', 'POST'])
def temp():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    cur = g.db.execute("SELECT * FROM temps ORDER BY timestamp DESC limit 12")
    templist = cur.fetchall()
    #data = {'Chrome':52.9,'Opera':1.6,'Firefox':27.7,}
    data = {}
    #此处有一个陷阱,解决时间>24h :(
    #从数据库中取得的数据中的字符串会自动转换为u""类型
    #但是chartkick要求的dict中字符串为str型
    #如果不做str()转换，数据无法读取
    #因为是纯数字字符串，所以不需要.decoce，直接str()即可
    for row in templist:
        data[str(row[0])] = row[1]
    #print tempdict
    #return str()
    return render_template('tmp.html', data = data)

@app.route("/timetable/",methods=['GET', 'POST'])
def timetable():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template('timetable.html')

if __name__ == "__main__":
    app.run("0.0.0.0",port = 80)