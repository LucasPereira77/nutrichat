# NutriChat - app.py
import os
import sqlite3
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = 'nutrichat2024'
DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'nutrichat.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' not in session:
        return None
    return get_db().execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

def calcular_imc(peso, altura):
    if not peso or not altura or altura <= 0 or peso <= 0:
        return None, None
    imc = peso / (altura ** 2)
    if imc < 18.5: cls = "Abaixo do peso"
    elif imc < 25.0: cls = "Peso normal"
    elif imc < 30.0: cls = "Sobrepeso"
    elif imc < 35.0: cls = "Obesidade grau I"
    elif imc < 40.0: cls = "Obesidade grau II"
    else: cls = "Obesidade grau III"
    return round(imc, 2), cls

def gerar_resposta(mensagem, user):
    msg = mensagem.lower()
    nome = user['nome'].split()[0]
    peso = user['peso']
    altura = user['altura']
    objetivo = user['objetivo'] or 'manter_peso'
    imc, cls_imc = calcular_imc(peso, altura)

    if any(p in msg for p in ['imc', 'calcul', 'peso ideal']):
        if imc:
            return f"Seu IMC e: {imc} - {cls_imc}\nPeso: {peso}kg | Altura: {altura}m\n\n{'Parabens! Voce esta no peso ideal!' if 18.5 <= imc < 25 else 'Com dedicacao voce vai atingir seu objetivo!'}"
        return f"Atualize seu peso e altura no perfil para calcular o IMC, {nome}!"

    if any(p in msg for p in ['dieta', 'plano', 'cardapio', 'o que comer', 'refeicao', 'refeição', 'cardápio']):
        if objetivo == 'emagrecer':
            return f"Plano para emagrecer, {nome}:\n\nCafe: 2 ovos + pao integral + fruta\nAlmoco: Arroz integral + feijao + frango + salada\nLanche: Iogurte + fruta\nJantar: Sopa ou omelete\n\nBeba 2L de agua por dia!"
        elif objetivo == 'ganhar_massa':
            return f"Plano para ganhar massa, {nome}:\n\nCafe: Vitamina de banana + aveia + 3 ovos\nAlmoco: Arroz + feijao + batata doce + frango\nPre-treino: Banana + pasta de amendoim\nJantar: Arroz integral + proteina"
        return f"Plano para manter peso, {nome}:\n\nCafe: Pao integral + queijo + fruta\nAlmoco: Arroz + feijao + proteina + salada\nLanche: Fruta + castanhas\nJantar: Refeicao leve"

    if any(p in msg for p in ['proteina', 'proteína', 'musculo', 'músculo']):
        return f"Fontes de proteina para voce, {nome}:\n\nAnimais: Frango, atum, ovos, iogurte grego\nVegetais: Feijao, lentilha, grao-de-bico, quinoa"

    if any(p in msg for p in ['agua', 'água', 'hidrata']):
        return f"Dicas de hidratacao, {nome}:\n\n- Beba 2 a 3 litros por dia\n- 1 copo em jejum ao acordar\n- Evite refrigerantes\n- Urina clara = bem hidratado!"

    if any(p in msg for p in ['lanche', 'snack']):
        return f"Lanches saudaveis, {nome}:\n\n- Fruta + castanhas\n- Iogurte com granola\n- Pao integral com pasta de amendoim\n- Ovo cozido\n- Tapioca com queijo"

    if any(p in msg for p in ['caloria', 'kcal']):
        if peso and altura and user['idade']:
            tmb = 88 + (13.4 * peso) + (4.8 * (altura * 100)) - (5.7 * user['idade'])
            meta = round(tmb * 1.3 - 500) if objetivo == 'emagrecer' else round(tmb * 1.5 + 300) if objetivo == 'ganhar_massa' else round(tmb * 1.4)
            return f"Estimativa de calorias, {nome}:\n\nMetabolismo basal: ~{round(tmb)} kcal/dia\nSua meta: ~{meta} kcal/dia"
        return f"Complete seu perfil com peso, altura e idade para calcular suas calorias, {nome}!"

    if any(p in msg for p in ['evitar', 'nao comer', 'não comer', 'ruim']):
        return f"Alimentos para evitar, {nome}:\n\n- Refrigerantes e sucos industriais\n- Fast food e frituras\n- Embutidos\n- Biscoitos recheados\n- Excesso de acucar e sal"

    if any(p in msg for p in ['emagrecer', 'perder peso']):
        return f"Dicas para emagrecer, {nome}:\n\n1. Deficit calorico moderado\n2. Priorize proteinas\n3. Coma fibras\n4. Beba agua\n5. Evite ultraprocessados\n6. Pratique exercicios\n7. Durma bem!"

    if any(p in msg for p in ['ganhar massa', 'hipertrofia', 'musculacao', 'musculação']):
        return f"Dicas para ganhar massa, {nome}:\n\n1. Consuma mais calorias\n2. Proteinas: 2g por kg de peso\n3. Carboidratos complexos\n4. Treine com progressao\n5. Descanse bem"

    if any(p in msg for p in ['oi', 'ola', 'olá', 'bom dia', 'boa tarde', 'boa noite']):
        return f"Ola {nome}! Sou a NutriBot! Posso te ajudar com:\n\n- Calcular IMC\n- Plano alimentar\n- Fontes de proteina\n- Lanches saudaveis\n- Calorias diarias\n- Dicas para emagrecer ou ganhar massa"

    if any(p in msg for p in ['obrigado', 'obrigada', 'valeu']):
        return f"Fico feliz em ajudar, {nome}! Cuide-se bem!"

    return f"Ola {nome}! Pergunte sobre:\n- IMC\n- Dieta\n- Proteinas\n- Lanches\n- Calorias\n- Emagrecer\n- Ganhar massa"

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user and user['senha_hash'] == hash_senha(senha):
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            db.execute('UPDATE users SET ultimo_login = ? WHERE id = ?', (datetime.now(), user['id']))
            db.commit()
            return redirect(url_for('chat'))
        error = "E-mail ou senha incorretos."
    return render_template('login.html', error=error)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    error = None
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar_senha', '')
        idade = request.form.get('idade', type=int)
        peso = request.form.get('peso', type=float)
        altura = request.form.get('altura', type=float)
        objetivo = request.form.get('objetivo', 'manter_peso')
        nivel_atividade = request.form.get('nivel_atividade', 'sedentario')
        if not nome or not email or not senha:
            error = "Preencha todos os campos."
        elif senha != confirmar:
            error = "As senhas nao coincidem."
        elif len(senha) < 6:
            error = "Senha deve ter 6 caracteres."
        else:
            db = get_db()
            if db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
                error = "E-mail ja cadastrado."
            else:
                db.execute('INSERT INTO users (nome, email, senha_hash, idade, peso, altura, objetivo, nivel_atividade) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (nome, email, hash_senha(senha), idade, peso, altura, objetivo, nivel_atividade))
                db.commit()
                user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
                session['user_id'] = user['id']
                session['user_nome'] = user['nome']
                if peso and altura:
                    imc, cls = calcular_imc(peso, altura)
                    db.execute('INSERT INTO imc_records (user_id, peso, altura, imc, classificacao) VALUES (?, ?, ?, ?, ?)',
                               (user['id'], peso, altura, imc, cls))
                    db.commit()
                return redirect(url_for('chat'))
    return render_template('cadastro.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    user = get_current_user()
    db = get_db()
    historico = list(reversed(db.execute(
        'SELECT role, message, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50',
        (session['user_id'],)).fetchall()))
    imc, classificacao = calcular_imc(user['peso'], user['altura'])
    evolucao = list(reversed(db.execute(
        'SELECT peso, imc, data_registro FROM imc_records WHERE user_id = ? ORDER BY data_registro DESC LIMIT 10',
        (session['user_id'],)).fetchall()))
    return render_template('chat.html', user=user, historico=historico, imc=imc, classificacao=classificacao, evolucao=evolucao)

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    mensagem = data.get('mensagem', '').strip()
    if not mensagem:
        return jsonify({'error': 'Mensagem vazia'}), 400
    user = get_current_user()
    db = get_db()
    db.execute('INSERT INTO conversations (user_id, role, message) VALUES (?, ?, ?)', (session['user_id'], 'user', mensagem))
    db.commit()
    resposta = gerar_resposta(mensagem, user)
    db.execute('INSERT INTO conversations (user_id, role, message) VALUES (?, ?, ?)', (session['user_id'], 'assistant', resposta))
    db.commit()
    return jsonify({'resposta': resposta})

@app.route('/api/atualizar-perfil', methods=['POST'])
@login_required
def atualizar_perfil():
    data = request.get_json()
    db = get_db()
    peso = float(data.get('peso', 0)) if data.get('peso') else None
    altura = float(data.get('altura', 0)) if data.get('altura') else None
    idade = int(data.get('idade', 0)) if data.get('idade') else None
    db.execute('UPDATE users SET peso=?, altura=?, idade=?, objetivo=?, nivel_atividade=? WHERE id=?',
               (peso, altura, idade, data.get('objetivo'), data.get('nivel_atividade'), session['user_id']))
    if peso and altura:
        imc, cls = calcular_imc(peso, altura)
        db.execute('INSERT INTO imc_records (user_id, peso, altura, imc, classificacao) VALUES (?, ?, ?, ?, ?)',
                   (session['user_id'], peso, altura, imc, cls))
    db.commit()
    imc, cls = calcular_imc(peso, altura) if peso and altura else (None, None)
    return jsonify({'success': True, 'imc': imc, 'classificacao': cls})

@app.route('/api/calcular-imc', methods=['POST'])
@login_required
def api_calcular_imc():
    data = request.get_json()
    imc, cls = calcular_imc(float(data.get('peso', 0)), float(data.get('altura', 0)))
    if imc:
        return jsonify({'imc': imc, 'classificacao': cls})
    return jsonify({'error': 'Dados invalidos'}), 400

@app.route('/api/evolucao')
@login_required
def api_evolucao():
    registros = get_db().execute(
        'SELECT peso, imc, classificacao, data_registro FROM imc_records WHERE user_id = ? ORDER BY data_registro ASC',
        (session['user_id'],)).fetchall()
    return jsonify([dict(r) for r in registros])

@app.route('/api/limpar-chat', methods=['POST'])
@login_required
def limpar_chat():
    get_db().execute('DELETE FROM conversations WHERE user_id = ?', (session['user_id'],))
    get_db().commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    print("NutriChat iniciando...")
    print("Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)