from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_do_grupo' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

# AQUI ESTÁ A MÁGICA: O comando de criar o banco agora está solto aqui em cima!
with app.app_context():
    db.create_all()

@app.route('/')
def tela_inicial():
    return render_template('login.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if len(senha) < 6:
        flash('Com uma senha dessas, até o gato andando no teclado consegue acessar seus livros. Exigimos no mínimo 6 caracteres!')
        return redirect('/')

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        flash('Este e-mail já está cadastrado. Tente fazer login!')
        return redirect('/')

    senha_criptografada = generate_password_hash(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha_hash=senha_criptografada)
    db.session.add(novo_usuario)
    db.session.commit()
    
    flash('Cadastro realizado com sucesso! Agora é só entrar.')
    return redirect('/')

@app.route('/login', methods=['POST'])
def fazer_login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.senha_hash, senha):
        session['usuario_id'] = usuario.id 
        return redirect('/catalogo')
    else:
        flash('Errou feio, errou rude! O e-mail ou a senha não batem. Tente novamente!')
        return redirect('/')

@app.route('/catalogo')
def catalogo():
    if 'usuario_id' not in session:
        flash('Ei! Você precisa fazer login antes de ver os livros.')
        return redirect('/')
    
    return render_template('catalogo.html')

@app.route('/meus_livros')
def meus_livros():
    if 'usuario_id' not in session:
        flash('Ei! Você precisa fazer login antes de ver seus livros.')
        return redirect('/')
    
    return render_template('meus_livros.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Você saiu do sistema com segurança.')
    return redirect('/')

# Veja que o final ficou bem mais limpo agora
if __name__ == '__main__':
    app.run(debug=True)