from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carros.sqlite'
app.config['SECRET_KEY'] = 'clave_secreta'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de la base de datos
class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(100), nullable=False)
    origen = db.Column(db.String(100), nullable=False)
    en_stock = db.Column(db.String(2), default="Sí")  # "Sí" o "No"

# Modelo de Usuario para login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

# Crear la base de datos
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="admin123")
        db.session.add(admin)
        db.session.commit()

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    carros = Carro.query.all()
    return render_template('index.html', carros=carros)

@app.route('/agregar', methods=['POST'])
@login_required
def agregar():
    marca = request.form.get('marca')
    origen = request.form.get('origen')

    if not marca or not origen:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('index'))

    nuevo_carro = Carro(marca=marca, origen=origen)
    db.session.add(nuevo_carro)
    db.session.commit()
    flash("Carro agregado con éxito.", "success")

    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    carro = Carro.query.get(id)
    if carro:
        db.session.delete(carro)
        db.session.commit()
        flash("Carro eliminado con éxito.", "success")
    else:
        flash("No se encontró el carro.", "danger")

    return redirect(url_for('index'))

@app.route('/cambiar_stock/<int:id>', methods=['POST'])
@login_required
def cambiar_stock(id):
    carro = Carro.query.get(id)
    if carro:
        carro.en_stock = "No" if carro.en_stock == "Sí" else "Sí"
        db.session.commit()
        flash("Estado de stock actualizado.", "info")
    else:
        flash("No se encontró el carro.", "danger")

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and User.check_password(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")  # Añadir un mensaje de cierre de sesión
    return redirect(url_for('logout_message'))  # Redirigir a la página de logout con el mensaje

@app.route('/logout_message')
def logout_message():
    return render_template('logout.html')  # Mostrar el mensaje de logout


@app.errorhandler(401)
def unauthorized_error(e):
    return redirect(url_for("login"))

@app.errorhandler(404)
def error_404(error):
    return render_template("error404.html"), 404

@app.route('/cv')
def cv():
    return render_template('cv.html')


if __name__ == '__main__':
    app.run(debug=True)
