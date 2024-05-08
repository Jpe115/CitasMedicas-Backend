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

@app.route("/api/doctores")
def get_doctores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT d.id, nombre, apellido, especialidadId, e.especialidad FROM doctores d INNER JOIN especialidades e ON d.especialidadId = e.id")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)

@app.route("/api/pacientes")
def get_pacientes():
    cur = mysql.connection.cursor()
    cur.execute("select * from pacientes")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)
@app.route("/api/especialidades")

def get_especialidades():
    cur = mysql.connection.cursor()
    cur.execute("select * from especialidades")
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)

@app.route("/api/citas/<string:año>/<string:mes>")
def get_citas(año, mes):
    if mes == "12":
        mes2 = "01"
        año2 = int(año) + 1
    else:
        mes2 = int(mes) + 1
        año2 = año
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.id, c.pacienteId, p.nombre, p.apellido, p.edad, c.doctorId, d.nombre, d.apellido, c.especialidadId, e.especialidad, c.fecha, c.hora FROM citas c INNER JOIN doctores d ON c.doctorId = d.id INNER JOIN pacientes p ON c.pacienteId = p.id INNER JOIN especialidades e ON c.especialidadId = e.id WHERE fecha >= '{0}-{1}-01' AND fecha < '{2}-{3}-01'".format(año, mes, año2, mes2))
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    return jsonify(json_data)

@app.route("/api/doctores/add", methods=["POST"])
def add_doctor():
    if request.method != "POST":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

    cur = mysql.connection.cursor()
    
    try:
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        especialidadId = request.form["especialidadId"]
        if nombre == "" or apellido == "" or especialidadId == "":
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        result = cur.execute("insert into doctores (nombre, apellido, especialidadId) values (%s, %s, %s)", (nombre, apellido, especialidadId))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Doctor añadido correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo añadir al doctor'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/pacientes/add", methods=["POST"])
def add_paciente():
    if request.method != "POST":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

    cur = mysql.connection.cursor()
    
    try:
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        if nombre == "" or apellido == "" or edad == "" or telefono == "" or correo == "":
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        result = cur.execute("insert into pacientes (nombre, apellido, edad, telefono, correo) values (%s, %s, %s, %s, %s)", (nombre, apellido, edad, telefono, correo))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Paciente añadido correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo añadir al paciente'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/especialidades/add", methods=["POST"])
def add_especialidad():
    if request.method != "POST":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

    cur = mysql.connection.cursor()
    
    try:
        especialidad = request.form["especialidad"]
        if especialidad == "":
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        result = cur.execute("insert into especialidades (especialidad) values (%s)", (especialidad))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Especialidad añadida correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo añadir la especialidad'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/citas/add", methods=["POST"])
def add_cita():
    if request.method != "POST":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

    cur = mysql.connection.cursor()
    
    try:
        doctorId = request.form["doctorId"]
        pacienteId = request.form["pacienteId"]
        especialidadId = request.form["especialidadId"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        if doctorId == "" or pacienteId == "" or especialidadId == "" or fecha == "" or hora == "":
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        result = cur.execute("insert into citas (doctorId, pacienteId, especialidadId, fecha, hora) values (%s, %s, %s, %s, %s)", (doctorId, pacienteId, especialidadId, fecha, hora))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Cita añadida correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo añadir la cita'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

# @app.route("/update/<id>", methods=["POST"])
# def update_contact(id):
#     if request.method == "POST":
#         fullname = request.form["fullname"]
#         email = request.form["email"]
#         phone = request.form["phone"]

#         cur = mysql.connection.cursor()
#         cur.execute("UPDATE contactss SET fullname = %s, email = %s, phone = %s WHERE id = %s", (fullname, email, phone, id))
#         mysql.connection.commit()

#         flash("Contact updated successfully")
#         return redirect(url_for("Index"))

@app.route("/api/doctores/delete/<string:id>")
def delete_doctor(id):
    cur = mysql.connection.cursor()
    try:
        # Ejecutando la sentencia SQL de DELETE
        result = cur.execute("DELETE FROM doctores WHERE id = %s", (id,))
        mysql.connection.commit()
        
        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Doctor eliminado correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se encontró el doctor para eliminar'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/pacientes/delete/<string:id>")
def delete_paciente(id):
    cur = mysql.connection.cursor()
    try:
        # Ejecutando la sentencia SQL de DELETE
        result = cur.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        mysql.connection.commit()
        
        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Paciente eliminado correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se encontró el paciente para eliminar'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/especialidades/delete/<string:id>")
def delete_especialidad(id):
    cur = mysql.connection.cursor()
    try:
        # Ejecutando la sentencia SQL de DELETE
        result = cur.execute("DELETE FROM especialidades WHERE id = %s", (id,))
        mysql.connection.commit()
        
        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Especialidad eliminada correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se encontró la especialidad para eliminar'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/citas/delete/<string:id>")
def delete_cita(id):
    cur = mysql.connection.cursor()
    try:
        # Ejecutando la sentencia SQL de DELETE
        result = cur.execute("DELETE FROM citas WHERE id = %s", (id,))
        mysql.connection.commit()
        
        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Cita eliminada correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se encontró la cita para eliminar'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)