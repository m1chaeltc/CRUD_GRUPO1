from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from datetime import datetime
import os
from flask import send_from_directory

app= Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)

#validaciones
app.secret_key="Grupo 1"

#modificar la foto del usuarios
CARPETA=os.path.join('uploads')
app.config['CARPETA']=CARPETA

#directorio de imagenes
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

#index
@app.route('/')
def index():

    sql ="SELECT * FROM empleados;"
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)

    empleados=cursor.fetchall()
    print(empleados)

    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

#eliminar usuario
@app.route('/destroy/<int:id>')
def destroy(id):
    conn=mysql.connect()
    cursor=conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id))
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
    conn.commit()

    return redirect('/') 

#editar usuario
@app.route('/edit/<int:id>')
def edit(id):

    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados=cursor.fetchall()
    conn.commit()
    print(empleados)

    return render_template('empleados/edit.html',  empleados=empleados)

#actualizar datos de usuario
@app.route('/update', methods=['post'])
def update():

    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtId']

    sql ="UPDATE empleados SET nombre=%s, correo=%s WHERE Id=%s ;"
    datos=(_nombre,_correo,id)
    conn= mysql.connect()
    cursor=conn.cursor()

    now= datetime.now()
    tiempo=now.strftime('%Y%H%M%S')

    if _foto.filename!='':

        newNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+newNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id))
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(newNombreFoto, id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')

#crear usuario
@app.route('/create')
def create():

    return render_template('empleados/create.html')

#crear almacenamiento de usuarios
@app.route('/store', methods=['POST'])
def storage():

    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']

    if _nombre=='' or _correo=='' or _foto=='':
        flash('Recuerda llenar los campos')
        return redirect(url_for('create'))

    now= datetime.now()
    tiempo=now.strftime('%Y%H%M%S')

    if _foto.filename!='':
        newNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+newNombreFoto)

    sql ="INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s, %s, %s);"
    
    datos=(_nombre,_correo,newNombreFoto)

    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

#if __name__== '__main__ ':
app.run('192.168.2.3', 5000, debug=True)