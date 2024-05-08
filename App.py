from flask import Flask, jsonify, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "agenda"
mysql = MySQL(app)

# MySQL
app.secret_key = "mysecretkey"

@app.route("/api/doctors")
def get_doctors():
    cur = mysql.connection.cursor()
    cur.execute("select * from doctores")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)

@app.route("/api/patients")
def get_patients():
    cur = mysql.connection.cursor()
    cur.execute("select * from pacientes")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)
@app.route("/api/consults")

def get_consults():
    cur = mysql.connection.cursor()
    cur.execute("select * from consultas")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)

@app.route("/api/appointments")
def get_appointments():
    cur = mysql.connection.cursor()
    cur.execute("select * from citas")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)

@app.route("/add_contact", methods=["POST"])
def add_contact():
    if request.method == "POST":
        fullname = request.form["fullname"]
        phone = request.form["phone"]
        email = request.form["email"]
        cur = mysql.connection.cursor()
        cur.execute("insert into contactss (fullname, phone, email) values (%s, %s, %s)", (fullname, phone, email))
        mysql.connection.commit()
        flash("Contact added")
        
        return redirect(url_for("Index"))

@app.route("/edit/<id>")
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute("select * from contactss where id = {0}".format(id))
    data = cur.fetchall()
    return render_template("edit-contact.html", contact = data[0])

@app.route("/update/<id>", methods=["POST"])
def update_contact(id):
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        phone = request.form["phone"]

        cur = mysql.connection.cursor()
        cur.execute("UPDATE contactss SET fullname = %s, email = %s, phone = %s WHERE id = %s", (fullname, email, phone, id))
        mysql.connection.commit()

        flash("Contact updated successfully")
        return redirect(url_for("Index"))

@app.route("/delete/<string:id>")
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute("delete from contactss where id = {0}".format(id))
    mysql.connection.commit()
    flash("Contact removed successfully")
    return redirect(url_for("Index"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)