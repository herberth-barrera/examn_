from flask import Flask, render_template_string, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="examen_fp"
    )


LISTA_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Tienda Mi Bodega</title></head>
<body>
  <h1>Productos - Tienda Mi Bodega</h1>
  <a href="{{ url_for('crear') }}">Nuevo producto</a>
  <table border="1" cellpadding="5">
    <tr>
      <th>ID</th><th>Nombre</th><th>Código de barras</th>
      <th>Categoría</th><th>Precio</th><th>Stock</th><th>Acciones</th>
    </tr>
    {% for p in productos %}
    <tr>
      <td>{{ p.id }}</td>
      <td>{{ p.nombre }}</td>
      <td>{{ p.codigo_barras or '' }}</td>
      <td>{{ p.categoria or '' }}</td>
      <td>{{ p.precio }}</td>
      <td>{{ p.stock }}</td>
      <td>
        <a href="{{ url_for('editar', id=p.id) }}">Editar</a>
        <form action="{{ url_for('eliminar', id=p.id) }}" method="post" style="display:inline">
          <button type="submit">Eliminar</button>
        </form>
      </td>
    </tr>
    {% else %}
    <tr><td colspan="7">No hay productos registrados.</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""

FORM_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{{ titulo }}</title></head>
<body>
  <h1>{{ titulo }}</h1>
  {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
  <form method="post">
    <p>Nombre: <input type="text" name="nombre" maxlength="100" required value="{{ p.nombre or '' }}"></p>
    <p>Código de barras: <input type="text" name="codigo_barras" maxlength="30" value="{{ p.codigo_barras or '' }}"></p>
    <p>Categoría: <input type="text" name="categoria" maxlength="50" value="{{ p.categoria or '' }}"></p>
    <p>Precio: <input type="number" name="precio" step="0.01" min="0" required value="{{ p.precio if p.precio is not none else '' }}"></p>
    <p>Stock: <input type="number" name="stock" step="1" min="0" value="{{ p.stock if p.stock is not none else 0 }}"></p>
    <button type="submit">Guardar</button>
    <a href="{{ url_for('listar') }}">Cancelar</a>
  </form>
</body>
</html>
"""


def leer_formulario():
    return {
        "nombre": request.form["nombre"].strip(),
        "codigo_barras": request.form.get("codigo_barras", "").strip() or None,
        "categoria": request.form.get("categoria", "").strip() or None,
        "precio": request.form["precio"],
        "stock": request.form.get("stock", "").strip() or 0,
    }


# LISTAR
@app.route("/")
def listar():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY id")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template_string(LISTA_HTML, productos=productos)


# CREAR
@app.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        p = leer_formulario()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre, codigo_barras, categoria, precio, stock) "
                "VALUES (%s, %s, %s, %s, %s)",
                (p["nombre"], p["codigo_barras"], p["categoria"], p["precio"], p["stock"])
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect(url_for("listar"))
        except mysql.connector.IntegrityError:
            return render_template_string(FORM_HTML, titulo="Nuevo producto", p=p,
                                          error="Ese código de barras ya existe.")
    return render_template_string(FORM_HTML, titulo="Nuevo producto", p={}, error=None)


# EDITAR
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        p = leer_formulario()
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE productos SET nombre=%s, codigo_barras=%s, categoria=%s, "
                "precio=%s, stock=%s WHERE id=%s",
                (p["nombre"], p["codigo_barras"], p["categoria"], p["precio"], p["stock"], id)
            )
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect(url_for("listar"))
        except mysql.connector.IntegrityError:
            return render_template_string(FORM_HTML, titulo="Editar producto", p=p,
                                          error="Ese código de barras ya existe.")

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conexion.close()
    if producto is None:
        return redirect(url_for("listar"))
    return render_template_string(FORM_HTML, titulo="Editar producto", p=producto, error=None)


# ELIMINAR
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for("listar"))


if __name__ == "__main__":
    app.run(debug=True)