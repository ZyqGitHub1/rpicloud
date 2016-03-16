import sqlite3
import os
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir,"db","user.db")
DATABASE = db_path
def connect_db():
    return sqlite3.connect(DATABASE)
data1 = {'Chrome':52.9,'Opera':1.6,'Firefox':27.7,}
db = connect_db()
cur = db.execute("select * from temps")
templist = cur.fetchall()
#data = {'Chrome':52.9,'Opera':1.6,'Firefox':27.7,}
data = {}  
for row in templist:
    data[str(row[0])] = row[1]
print templist
print data
print data1
#return str()
#return render_template('tmp.html', data = data)
cur.close()
db.close()