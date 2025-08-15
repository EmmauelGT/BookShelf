import os, re
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Book

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        SQLALCHEMY_DATABASE_URI="sqlite:///BookShelf.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))

    # ---------- Auth ----------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            birth_date_str = request.form.get("birth_date", "")

            if not all([username, email, password, birth_date_str]):
                flash("Todos los campos son obligatorios.", "danger")
                return redirect(url_for("register"))

            # fecha de nacimiento -> edad >= 18
            try:
                birth = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Fecha de nacimiento inválida.", "danger"); return redirect(url_for("register"))
            age = (date.today() - birth).days // 365
            if age < 18:
                flash("Debes ser mayor de 18 años.", "danger"); return redirect(url_for("register"))

            # política de contraseña
            pw_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"
            if not re.match(pw_pattern, password):
                flash("La contraseña no cumple la política de seguridad.", "danger")
                return redirect(url_for("register"))

            if User.query.filter_by(username=username).first():
                flash("El usuario ya existe.", "danger"); return redirect(url_for("register"))
            if User.query.filter_by(email=email).first():
                flash("El correo ya está registrado.", "danger"); return redirect(url_for("register"))

            user = User(username=username, email=email, birth_date=birth)
            user.set_password(password)
            db.session.add(user); db.session.commit()
            flash("Cuenta creada. Inicia sesión.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash("Usuario o contraseña incorrectos.", "danger")
                return render_template("login.html")
            session.clear()
            session["user_id"] = user.id
            session.permanent = True
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Sesión cerrada.", "info")
        return redirect(url_for("login"))

    # ---------- Books ----------
    def _require_login():
        if not session.get("user_id"):
            return redirect(url_for("login"))

    @app.route("/dashboard")
    def dashboard():
        if not session.get("user_id"): return redirect(url_for("login"))
        user = User.query.get(session["user_id"])
        books = Book.query.filter_by(user_id=user.id).all()
        return render_template("dashboard.html", user=user, books=books)

    @app.route("/add_book", methods=["GET", "POST"])
    def add_book():
        if not session.get("user_id"): return redirect(url_for("login"))
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            author = request.form.get("author", "").strip()
            status = request.form.get("status", "Pendiente")
            if not title or not author:
                flash("Título y autor son obligatorios.", "danger")
                return redirect(url_for("add_book"))
            book = Book(title=title, author=author, status=status, user_id=session["user_id"])
            db.session.add(book); db.session.commit()
            flash("Libro agregado.", "success")
            return redirect(url_for("dashboard"))
        return render_template("add_book.html", book=None)

    @app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
    def edit_book(book_id):
        if not session.get("user_id"): return redirect(url_for("login"))
        book = Book.query.get_or_404(book_id)
        if book.user_id != session["user_id"]:
            flash("No autorizado.", "danger"); return redirect(url_for("dashboard"))
        if request.method == "POST":
            book.title = request.form.get("title", "").strip()
            book.author = request.form.get("author", "").strip()
            book.status = request.form.get("status", "Pendiente")
            db.session.commit()
            flash("Libro actualizado.", "success")
            return redirect(url_for("dashboard"))
        return render_template("add_book.html", book=book)

    @app.route("/delete_book/<int:book_id>", methods=["POST", "GET"])
    def delete_book(book_id):
        if not session.get("user_id"): return redirect(url_for("login"))
        book = Book.query.get_or_404(book_id)
        if book.user_id != session["user_id"]:
            flash("No autorizado.", "danger"); return redirect(url_for("dashboard"))
        db.session.delete(book); db.session.commit()
        flash("Libro eliminado.", "success")
        return redirect(url_for("dashboard"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    