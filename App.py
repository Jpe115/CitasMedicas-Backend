from flask import Flask, jsonify, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    
    cur.close()
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
    
    cur.close()
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
    
    cur.close()
    return jsonify(json_data)

@app.route("/api/citas/<string:year>/<string:mes>")
def get_citas(year, mes):
    if mes == "12":
        mes2 = "01"
        año2 = int(year) + 1
    else:
        mes2 = int(mes) + 1
        año2 = year
    cur = mysql.connection.cursor()
    cur.execute("SELECT c.id, c.pacienteId, p.nombre AS nombrePaciente, p.apellido AS apellidoPaciente, p.edad, c.doctorId, d.nombre AS nombreDoctor, d.apellido AS apellidoDoctor, c.especialidadId, e.especialidad, c.fecha, c.hora FROM citas c INNER JOIN doctores d ON c.doctorId = d.id INNER JOIN pacientes p ON c.pacienteId = p.id INNER JOIN especialidades e ON c.especialidadId = e.id WHERE fecha >= '{0}-{1}-01' AND fecha < '{2}-{3}-01' ORDER BY c.hora".format(year, mes, año2, mes2))
    data = cur.fetchall()
    # Convertir las tuplas a una lista de diccionarios
    row_headers = [x[0] for x in cur.description]  # Esto captura los nombres de las columnas
    json_data = []
    for result in data:
        json_data.append(dict(zip(row_headers, result)))
    
    cur.close()
    return jsonify(json_data)

@app.route("/api/doctores/add", methods=["POST"])
def add_doctor():
    if request.method != "POST":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    
    try:
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        especialidadId = request.form["especialidadId"]
        if not nombre or not apellido or not especialidadId:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        #Comprobar que no sea repetido
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM doctores WHERE nombre = %s AND apellido = %s AND especialidadId = %s", (nombre, apellido, especialidadId))
        doctor = cur.fetchone()
        if doctor:
            return jsonify({'success': False, 'message': 'Los datos del doctor ya existen'}), 400

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
    
    try:
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        if not nombre or not apellido or not edad or not telefono or not correo:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500
        
        #Verificar repetidos
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pacientes WHERE nombre = %s AND apellido = %s AND edad = %s AND telefono = %s AND correo = %s", (nombre, apellido, edad, telefono, correo))
        paciente = cur.fetchone()
        if paciente:
            return jsonify({'success': False, 'message': 'Los datos del paciente ya existen'}), 400

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
    
    try:
        especialidad = request.form["especialidad"]
        if not especialidad:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM especialidades WHERE especialidad = %s", (especialidad,))
        especialidad_encontrada = cur.fetchone()
        if especialidad_encontrada:
            return jsonify({'success': False, 'message': 'Los datos de la especialidad ya existen'}), 400

        result = cur.execute("insert into especialidades (especialidad) values (%s)", (especialidad,))
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
    
    try:
        doctorId = request.form["doctorId"]
        pacienteId = request.form["pacienteId"]
        especialidadId = request.form["especialidadId"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        if not doctorId or not pacienteId or not especialidadId or not fecha or not hora:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM citas WHERE doctorId = %s AND pacienteId = %s AND especialidadId = %s AND fecha = %s AND hora = %s", (doctorId, pacienteId, especialidadId, fecha, hora))
        cita = cur.fetchone()
        if cita:
            return jsonify({'success': False, 'message': 'Los datos de la cita ya existen'}), 400

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

@app.route("/api/doctores/update", methods=["PUT"])
def update_doctor():
    if request.method != "PUT":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    
    try:
        id = request.form["id"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        especialidadId = request.form["especialidadId"]
        if not id or not nombre or not apellido or not especialidadId:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        #Comprobar que exista antes de update
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM doctores WHERE id = %s", (id,))
        doctor = cur.fetchone()
        if not doctor:
            return jsonify({'success': False, 'message': 'No existe el doctor solicitado'}), 400

        result = cur.execute("UPDATE doctores SET nombre = %s, apellido = %s, especialidadId = %s WHERE id = %s", (nombre, apellido, especialidadId, id))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Doctor actualizado correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo actualizar al doctor. Datos ingresados idénticos'}), 404
    except Exception as e:
        # En caso de una excepción, hacemos rollback y devolvemos error
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()  # Asegurándonos de cerrar el cursor

@app.route("/api/pacientes/update", methods=["PUT"])
def update_paciente():
    if request.method != "PUT":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    
    try:
        id = request.form["id"]
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]
        if not id or not nombre or not apellido or not edad or not telefono or not correo:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        #Comprobar que exista antes de update
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
        paciente = cur.fetchone()
        if not paciente:
            return jsonify({'success': False, 'message': 'No existe el paciente solicitado'}), 400

        result = cur.execute("UPDATE pacientes SET nombre = %s, apellido = %s, edad = %s, telefono = %s, correo = %s WHERE id = %s", (nombre, apellido, edad, telefono, correo, id))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Paciente actualizado correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo actualizar al paciente. Datos ingresados idénticos'}), 404
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()

@app.route("/api/citas/update", methods=["PUT"])
def update_cita():
    if request.method != "PUT":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    
    try:
        id = request.form["id"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]
        if not id  or not fecha or not hora:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        #Comprobar que exista antes de update
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM citas WHERE id = %s", (id,))
        cita = cur.fetchone()
        if not cita:
            return jsonify({'success': False, 'message': 'No existe la cita solicitada'}), 400

        result = cur.execute("UPDATE citas SET fecha = %s, hora = %s WHERE id = %s", (fecha, hora, id))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Cita actualizada correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo actualizar la cita. Datos ingresados idénticos'}), 404
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()

@app.route("/api/especialidades/update", methods=["PUT"])
def update_especialidad():
    if request.method != "PUT":
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
    
    try:
        id = request.form["id"]
        especialidad = request.form["especialidad"]
        if not id or not especialidad:
            return jsonify({'success': False, 'message': 'Datos faltantes o erróneos'}), 500

        #Comprobar que exista antes de update
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM especialidades WHERE id = %s", (id,))
        especialidad_encontrada = cur.fetchone()
        if not especialidad_encontrada:
            return jsonify({'success': False, 'message': 'No existe la especialidad solicitada'}), 400

        result = cur.execute("UPDATE especialidades SET especialidad = %s WHERE id = %s", (especialidad, id))
        mysql.connection.commit()

        # Verificando si algún registro fue afectado
        if result > 0:
            return jsonify({'success': True, 'message': 'Especialidad actualizada correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se pudo actualizar la especialidad. Datos ingresados idénticos'}), 404
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()

@app.route("/api/doctores/delete/<string:id>", methods=["DELETE"])
def delete_doctor(id):
    try:
        if id is None:
            return jsonify({'success': False, 'message': 'Se requiere el parámetro "id"'})
        
        cur = mysql.connection.cursor()
        result = cur.execute("DELETE FROM doctores WHERE id = %s", (id,))
        mysql.connection.commit()

        if result > 0:
            return jsonify({'success': True, 'message': 'Doctor eliminado correctamente'}), 200
        else:
            return jsonify({'success': False, 'message': 'No se encontró el doctor para eliminar'}), 404
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()

@app.route("/api/pacientes/delete/<string:id>", methods=["DELETE"])
def delete_paciente(id):
    cur = mysql.connection.cursor()
    try:
        if id is None:
            return jsonify({'success': False, 'message': 'Se requiere el parámetro "id"'})

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

@app.route("/api/especialidades/delete/<string:id>", methods=["DELETE"])
def delete_especialidad(id):
    cur = mysql.connection.cursor()
    try:
        if id is None:
            return jsonify({'success': False, 'message': 'Se requiere el parámetro "id"'})

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

@app.route("/api/citas/delete/<string:id>", methods=["DELETE"])
def delete_cita(id):
    cur = mysql.connection.cursor()
    try:
        if id is None:
            return jsonify({'success': False, 'message': 'Se requiere el parámetro "id"'})

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