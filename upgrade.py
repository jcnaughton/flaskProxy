from flask import Flask
from flask import request
from flask import url_for
import sqlite3
import requests

app = Flask(__name__)

@app.route("/")
def welcome():
    url_for('static', filename='bootstrap.min.css')
    url_for('static', filename='bootstrap.bundle.min.js')
    html = "<!doctype html>"
    html += "<html lang=\"en\">"
    html += "<head>"
    html += "<meta charset=\"utf-8\">"
    html += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    html += "<title>Bootstrap demo</title>"
    html += "<link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/icon?family=Material+Icons\">"
    html += "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.min.css\">"
    html += "<link href=\"/static/bootstrap.min.css\" rel=\"stylesheet\">"
    html += "<body class=\"bg-secondary\">"
    html += "<h1 class=\"bg-dark text-light\">upgrade</h1>"
    html += "<form action=\"/table\" method=\"post\">"
    html += "three octects<input type=\"text\" name=\"threeOctets\" value=\"X.X.X\">"
    html += "first host<input type=\"text\" name=\"firstHost\" value=\"16\">"
    html += "last host<input type=\"text\" name=\"lastHost\" value=\"255\">"
    html += "<button type=\"submit\" class=\"btn btn-primary\">create new table</button></form>"
    html += "<a href=\"/preCheck\"><button type=\"button\" class=\"btn btn-success\">scan subnet</button></a>"
    html += "<a href=\"/upgrade\"><button type=\"button\" class=\"btn btn-warning\">upgrade</button></a>"
    html += "<a href=\"/postCheck\"><button type=\"button\" class=\"btn btn-danger\">post upgrade scan</button></a>"
    html += "<table class=\"table table-striped\">"
    html += "<tr><th>ip</th><th>macPre</th><th>verPre</th><th>macPost</th><th>verPost</th><tr>"
    con = sqlite3.connect('upgrade.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute("SELECT * FROM subnet;")
    for row in res.fetchall():
        if row['verPre'] != None:
            html += "<tr>"
            html += "<td>" + str(row['ip']) + "</td><td>" + str(row['macPre']) + "</td><td>" + str(row['verPre']) + "</td>"
            html += "<td>" + str(row['macPost']) + "</td><td>" + str(row['verPost']) + "</td>"
            html += "</tr>"
    html += "</table>"
    html += "<script src=\"/static/bootstrap.bundle.min.js\"></script>"
    html += "</body>"
    html += "</html>"
    return html

@app.route("/table",methods=['POST'])
def mkTable():
    html = "<!doctype html>"
    con = sqlite3.connect("upgrade.db")
    cur = con.cursor()
    cur.execute("DROP TABLE subnet;")
    con.commit()
    cur.execute("CREATE TABLE subnet (ip TEXT, macPre TEXT, verPre TEXT, macPost TEXT, verPost TEXT);")
    con.commit()
    for host in range(int(request.form['firstHost']),int(request.form['lastHost'])):
        newIp = str(request.form['threeOctets']) + "." + str(host)
        cur.execute("INSERT INTO subnet (ip) VALUES ('" + newIp + "');")
        con.commit()
    html += "<meta http-equiv=\"refresh\" content=\"0; url=/\">"
    return html

@app.route("/preCheck",methods=['GET'])
def preCheck():
    con = sqlite3.connect('upgrade.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute("SELECT * FROM subnet;")
    for row in res.fetchall():
        url = "http://" + str(row['ip']) + "/api/"
        try:
            r = requests.get(url,timeout=1)
            print( url + r.json()['ver'] )
            #print("UPDATE subnet SET verPre = '" + r.json()['ver'] + "' WHERE ip = '" + str(row['ip']) + "';")
            cur.execute("UPDATE subnet SET verPre = '" + r.json()['ver'] + "',macPre = '" + r.json()['mac'] + "' WHERE ip = '" + str(row['ip']) + "';")
            con.commit()
        except:
            print(url)
    return "<meta http-equiv=\"refresh\" content=\"0; url=/\">"

@app.route("/upgrade",methods=['GET'])
def upgrade():
    f = open("imdUpgrade.bat","w")
    con = sqlite3.connect('upgrade.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute("SELECT * FROM subnet;")
    for row in res.fetchall():
        if row['verPre'] != None:
            if str(row['verPre']) != '5.10.8':
                f.write("python fwupgrade.py --ip " + str(row['ip']) + "\n")
    return "<meta http-equiv=\"refresh\" content=\"0; url=/\">"

@app.route("/postCheck",methods=['GET'])
def postCheck():
    con = sqlite3.connect('upgrade.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute("SELECT * FROM subnet;")
    for row in res.fetchall():
        url = "http://" + str(row['ip']) + "/api/"
        try:
            r = requests.get(url,timeout=1)
            print( url + r.json()['ver'] )
            #print("UPDATE subnet SET verPre = '" + r.json()['ver'] + "' WHERE ip = '" + str(row['ip']) + "';")
            cur.execute("UPDATE subnet SET verPost = '" + r.json()['ver'] + "',macPost = '" + r.json()['mac'] + "' WHERE ip = '" + str(row['ip']) + "';")
            con.commit()
        except:
            print(url)
    return "<meta http-equiv=\"refresh\" content=\"0; url=/\">"
