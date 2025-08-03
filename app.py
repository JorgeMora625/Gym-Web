from flask import Flask, redirect, render_template, request, url_for
import mysql.connector  # type: ignore
from flask_mysqldb import MySQL  # type: ignore

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'BDGYM'

mysql = MySQL(app)



def obtener_datos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, peso, altura, dia FROM Persona")
    datos = cursor.fetchall()
    cursor.close()
    return datos

@app.route('/')
def index():
    persona = obtener_datos()
    return render_template('index.html', persona=persona)


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/home/grupos-musculares')
def obtener_columnas():
    cur = mysql.connection.cursor()
    cur.execute("SHOW TABLES")
    tablas = cur.fetchall()
    cur.close()
    nombre_tablas = [t[0] for t in tablas]
    return render_template('tablas.html', tablas=nombre_tablas)


@app.route('/home/grupos-musculares/<nombre>')
def mostrar_datos_tabla(nombre):
    cur = mysql.connection.cursor()
    try:
        cur.execute(f"SELECT * FROM {nombre} ORDER BY fecha DESC")
        datos = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
    except Exception as e:
        datos = []
        columnas = []
        print(f"Error al consultar la tabla {nombre}: {e}")
    cur.close()

    return render_template('datos_tabla.html', tabla=nombre, columnas=columnas, datos=datos)


@app.route('/home/grupos-musculares/<nombre>/nuevo', methods=['GET'])
def formulario_nuevo_registro(nombre):
    cur = mysql.connection.cursor()
    cur.execute(f"SHOW COLUMNS FROM {nombre}")
    columnas = [col[0] for col in cur.fetchall()]
    cur.close()
    return render_template('nuevo_registro.html', nombre=nombre, columnas=columnas)


@app.route('/home/grupos-musculares/<nombre>/guardar', methods=['POST'])
def guardar_registro(nombre):
    cur = mysql.connection.cursor()
    columnas = request.form.keys()
    valores = [request.form[col] for col in columnas]
    placeholders = ', '.join(['%s'] * len(valores))
    nombres_columnas = ', '.join(columnas)

    consulta = f"INSERT INTO `{nombre}` ({nombres_columnas}) VALUES ({placeholders})"
    cur.execute(consulta, valores)
    mysql.connection.commit()
    #cur.commit()
    cur.close()

    return redirect(url_for('mostrar_datos_tabla', nombre=nombre))


@app.route('/home/grupos-musculares/buscar', methods=['GET', 'POST'])
def buscar_levantamiento():
    resultados = None
    mensaje = None

    if request.method == 'POST':
        grupo = request.form.get('grupo')
        fecha = request.form.get('fecha')
        ejercicio = request.form.get('ejercicio')
        peso = request.form.get('peso')
        repes = request.form.get('repes')

        tablas_validas = ['pecho', 'espalda', 'pierna', 'biceps', 'triceps', 'hombro']
        if grupo not in tablas_validas:
            mensaje = "Grupo muscular no válido."
            return render_template("buscar.html", mensaje=mensaje)

        condiciones = []
        valores = []

        if fecha:
            condiciones.append("fecha = %s")
            valores.append(fecha)

        if ejercicio:
            condiciones.append("ejercicio LIKE %s")
            valores.append(f"%{ejercicio}%")

        if peso:
            condiciones.append("peso = %s")
            valores.append(peso)

        if repes:
            condiciones.append("repes = %s")
            valores.append(repes)

        sql = f"SELECT * FROM {grupo}"
        if condiciones:
            sql += " WHERE " + " AND ".join(condiciones)

        cur = mysql.connection.cursor()
        cur.execute(sql, valores)
        rows = cur.fetchall()
        cur.close()

        if rows:
            resultados = [
                {
                    'personaID': row[0],
                    'ejercicio': row[1],
                    'peso': row[2],
                    'repes': row[3],
                    'fecha': row[4]
                }
                for row in rows
            ]
        else:
            mensaje = "No se encontraron resultados."

    return render_template("buscar.html", resultados=resultados, mensaje=mensaje)






if __name__ == '__main__':
    app.run(debug=True)
