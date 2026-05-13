# ============================================================
# NutriChat - app.py
# Aplicação Flask principal do chatbot nutricional
# ============================================================

import os
from dotenv import load_dotenv
load_dotenv()
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, g
)
import google.generativeai as genai

# ----------------------------------------------------------
# Configuração da Aplicação
# ----------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Caminho do banco de dados SQLite
DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'nutrichat.db')

# Cliente Gemini (Google)
genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# ----------------------------------------------------------
# Funções de Banco de Dados
# ----------------------------------------------------------

def get_db():
    """Retorna conexão com o banco de dados, criando se necessário."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Resultados como dicionários
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Fecha conexão com banco ao final de cada requisição."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Inicializa o banco de dados com o schema SQL."""
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    with app.app_context():
        db = get_db()
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
    print("✅ Banco de dados inicializado com sucesso!")

# ----------------------------------------------------------
# Helpers de Autenticação
# ----------------------------------------------------------

def hash_senha(senha):
    """Gera hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()

def login_required(f):
    """Decorator que exige autenticação para acessar a rota."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """Retorna os dados do usuário logado."""
    if 'user_id' not in session:
        return None
    db = get_db()
    return db.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()

# ----------------------------------------------------------
# Cálculos Nutricionais
# ----------------------------------------------------------

def calcular_imc(peso, altura):
    """
    Calcula o IMC e retorna valor + classificação.
    IMC = peso(kg) / altura(m)²
    """
    if altura <= 0 or peso <= 0:
        return None, None
    imc = peso / (altura ** 2)
    
    if imc < 18.5:
        classificacao = "Abaixo do peso"
    elif imc < 25.0:
        classificacao = "Peso normal"
    elif imc < 30.0:
        classificacao = "Sobrepeso"
    elif imc < 35.0:
        classificacao = "Obesidade grau I"
    elif imc < 40.0:
        classificacao = "Obesidade grau II"
    else:
        classificacao = "Obesidade grau III"
    
    return round(imc, 2), classificacao

def calcular_tmb(peso, altura_cm, idade, sexo='masculino'):
    """
    Calcula a Taxa Metabólica Basal (Fórmula de Harris-Benedict revisada).
    """
    if sexo == 'masculino':
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura_cm) - (5.677 * idade)
    else:
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura_cm) - (4.330 * idade)
    return round(tmb)

# ----------------------------------------------------------
# Sistema de Prompt do Chatbot
# ----------------------------------------------------------

def build_system_prompt(user):
    """
    Constrói o prompt de sistema personalizado com os dados do usuário.
    """
    imc, classificacao = None, None
    if user['peso'] and user['altura']:
        imc, classificacao = calcular_imc(user['peso'], user['altura'])

    objetivos = {
        'emagrecer': 'perder peso de forma saudável e sustentável',
        'ganhar_massa': 'ganhar massa muscular com alimentação adequada',
        'manter_peso': 'manter o peso atual com hábitos saudáveis'
    }
    objetivo_texto = objetivos.get(user['objetivo'], 'manter uma alimentação equilibrada')

    perfil = f"""
    - Nome: {user['nome']}
    - Idade: {user['idade']} anos
    - Peso atual: {user['peso']} kg
    - Altura: {user['altura']} m
    - IMC: {imc} ({classificacao})
    - Objetivo: {objetivo_texto}
    - Nível de atividade: {user['nivel_atividade']}
    """ if user['peso'] and user['altura'] else f"""
    - Nome: {user['nome']}
    - Perfil nutricional ainda não completo
    """

    return f"""Você é a NutriBot, uma nutricionista virtual especializada e carinhosa do sistema NutriChat.

PERFIL DO USUÁRIO:
{perfil}

SUAS RESPONSABILIDADES:
1. Dar orientações nutricionais personalizadas e baseadas no perfil acima
2. Sugerir alimentos saudáveis, refeições balanceadas e lanches nutritivos
3. Calcular e explicar o IMC quando solicitado
4. Criar planos alimentares básicos conforme o objetivo do usuário
5. Motivar o usuário em sua jornada de saúde
6. Responder dúvidas sobre nutrição, vitaminas, minerais e macronutrientes
7. Recomendar hábitos alimentares saudáveis

REGRAS DE COMPORTAMENTO:
- Seja sempre amigável, motivador e acolhedor
- Use linguagem simples e acessível, evitando jargões excessivos
- Personalize as respostas usando o nome do usuário quando apropriado
- Sempre mencione que consultas presenciais com nutricionista são importantes para planos detalhados
- Nunca substitua um profissional de saúde
- Quando sugerir refeições, seja específico com alimentos, quantidades e horários
- Use emojis com moderação para tornar a conversa mais agradável
- Se o usuário não tiver perfil completo, incentive-o a atualizar seus dados

IDIOMA: Sempre responda em português brasileiro.

Seja a nutricionista virtual que as pessoas merecem: científica, prática e humana! 🥗"""

# ----------------------------------------------------------
# Rotas de Autenticação
# ----------------------------------------------------------

@app.route('/')
def index():
    """Página inicial - redireciona para chat ou login."""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página e lógica de login."""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if user and user['senha_hash'] == hash_senha(senha):
            # Login bem-sucedido
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            # Atualiza último login
            db.execute(
                'UPDATE users SET ultimo_login = ? WHERE id = ?',
                (datetime.now(), user['id'])
            )
            db.commit()
            return redirect(url_for('chat'))
        else:
            error = "E-mail ou senha incorretos. Tente novamente."
    
    return render_template('login.html', error=error)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página e lógica de cadastro."""
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

        # Validações básicas
        if not nome or not email or not senha:
            error = "Preencha todos os campos obrigatórios."
        elif senha != confirmar:
            error = "As senhas não coincidem."
        elif len(senha) < 6:
            error = "A senha deve ter pelo menos 6 caracteres."
        else:
            db = get_db()
            # Verifica se email já existe
            existing = db.execute(
                'SELECT id FROM users WHERE email = ?', (email,)
            ).fetchone()
            
            if existing:
                error = "Este e-mail já está cadastrado."
            else:
                # Insere novo usuário
                db.execute(
                    '''INSERT INTO users 
                       (nome, email, senha_hash, idade, peso, altura, objetivo, nivel_atividade)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nome, email, hash_senha(senha), idade, peso, altura, objetivo, nivel_atividade)
                )
                db.commit()
                # Faz login automático
                user = db.execute(
                    'SELECT * FROM users WHERE email = ?', (email,)
                ).fetchone()
                session['user_id'] = user['id']
                session['user_nome'] = user['nome']
                
                # Registra IMC inicial se dados fornecidos
                if peso and altura:
                    imc, classificacao = calcular_imc(peso, altura)
                    db.execute(
                        '''INSERT INTO imc_records (user_id, peso, altura, imc, classificacao)
                           VALUES (?, ?, ?, ?, ?)''',
                        (user['id'], peso, altura, imc, classificacao)
                    )
                    db.commit()
                
                return redirect(url_for('chat'))
    
    return render_template('cadastro.html', error=error)

@app.route('/logout')
def logout():
    """Faz logout do usuário."""
    session.clear()
    return redirect(url_for('login'))

# ----------------------------------------------------------
# Rota Principal do Chat
# ----------------------------------------------------------

@app.route('/chat')
@login_required
def chat():
    """Página principal do chatbot."""
    user = get_current_user()
    db = get_db()
    
    # Busca histórico das últimas 50 mensagens
    historico = db.execute(
        '''SELECT role, message, timestamp FROM conversations
           WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50''',
        (session['user_id'],)
    ).fetchall()
    historico = list(reversed(historico))  # Ordem cronológica
    
    # Calcula IMC atual
    imc, classificacao = None, None
    if user['peso'] and user['altura']:
        imc, classificacao = calcular_imc(user['peso'], user['altura'])
    
    # Busca evolução de peso (últimos 10 registros)
    evolucao = db.execute(
        '''SELECT peso, imc, data_registro FROM imc_records
           WHERE user_id = ? ORDER BY data_registro DESC LIMIT 10''',
        (session['user_id'],)
    ).fetchall()
    
    return render_template('chat.html',
        user=user,
        historico=historico,
        imc=imc,
        classificacao=classificacao,
        evolucao=list(reversed(evolucao))
    )

# ----------------------------------------------------------
# API do Chatbot (Claude)
# ----------------------------------------------------------

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """
    Endpoint da API que processa mensagens e retorna resposta da IA.
    Usa a API da Anthropic (Claude) para gerar respostas inteligentes.
    """
    data = request.get_json()
    mensagem = data.get('mensagem', '').strip()
    
    if not mensagem:
        return jsonify({'error': 'Mensagem vazia'}), 400
    
    user = get_current_user()
    db = get_db()
    
    # Salva mensagem do usuário no banco
    db.execute(
        'INSERT INTO conversations (user_id, role, message) VALUES (?, ?, ?)',
        (session['user_id'], 'user', mensagem)
    )
    db.commit()
    
    # Busca histórico recente para contexto (últimas 20 mensagens)
    historico_db = db.execute(
        '''SELECT role, message FROM conversations
           WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20''',
        (session['user_id'],)
    ).fetchall()
    
    # Monta histórico no formato da API (excluindo a mensagem atual)
    messages = []
    for msg in reversed(list(historico_db)[1:]):  # Remove a última (atual)
        role = 'user' if msg['role'] == 'user' else 'assistant'
        messages.append({'role': role, 'content': msg['message']})
    
    # Adiciona a mensagem atual do usuário
    messages.append({'role': 'user', 'content': mensagem})
    
    try:
        # Monta o histórico no formato do Gemini
        historico_gemini = []
        for msg in messages[:-1]:  # Todos exceto o último
            historico_gemini.append({
                'role': 'user' if msg['role'] == 'user' else 'model',
                'parts': [msg['content']]
            })

        # Prompt completo = system prompt + mensagem atual
        prompt_completo = build_system_prompt(user) + '\n\nUsuário: ' + mensagem

        # Chama a API do Gemini
        chat = gemini_model.start_chat(history=historico_gemini)
        response = chat.send_message(prompt_completo)
        resposta = response.text

        # Salva resposta da IA no banco
        db.execute(
            'INSERT INTO conversations (user_id, role, message) VALUES (?, ?, ?)',
            (session['user_id'], 'assistant', resposta)
        )
        db.commit()

        return jsonify({'resposta': resposta})

    except Exception as e:
        print(f"Erro na API Gemini: {e}")
        return jsonify({'error': 'Erro ao processar sua mensagem. Tente novamente.'}), 500

# ----------------------------------------------------------
# API de Perfil e IMC
# ----------------------------------------------------------

@app.route('/api/atualizar-perfil', methods=['POST'])
@login_required
def atualizar_perfil():
    """Atualiza os dados do perfil do usuário."""
    data = request.get_json()
    db = get_db()
    
    peso = data.get('peso', type=float) if isinstance(data.get('peso'), (int, float)) else float(data.get('peso', 0))
    altura = data.get('altura', type=float) if isinstance(data.get('altura'), (int, float)) else float(data.get('altura', 0))
    
    # Corrige leitura dos dados JSON
    peso = float(data.get('peso', 0)) if data.get('peso') else None
    altura = float(data.get('altura', 0)) if data.get('altura') else None
    idade = int(data.get('idade', 0)) if data.get('idade') else None
    objetivo = data.get('objetivo')
    nivel_atividade = data.get('nivel_atividade')
    
    db.execute(
        '''UPDATE users SET peso=?, altura=?, idade=?, objetivo=?, nivel_atividade=?
           WHERE id=?''',
        (peso, altura, idade, objetivo, nivel_atividade, session['user_id'])
    )
    
    # Registra novo IMC se tiver peso e altura
    if peso and altura:
        imc, classificacao = calcular_imc(peso, altura)
        db.execute(
            '''INSERT INTO imc_records (user_id, peso, altura, imc, classificacao)
               VALUES (?, ?, ?, ?, ?)''',
            (session['user_id'], peso, altura, imc, classificacao)
        )
    
    db.commit()
    
    imc, classificacao = calcular_imc(peso, altura) if peso and altura else (None, None)
    return jsonify({
        'success': True,
        'imc': imc,
        'classificacao': classificacao
    })

@app.route('/api/calcular-imc', methods=['POST'])
@login_required
def api_calcular_imc():
    """Calcula o IMC com base nos dados fornecidos."""
    data = request.get_json()
    peso = float(data.get('peso', 0))
    altura = float(data.get('altura', 0))
    
    imc, classificacao = calcular_imc(peso, altura)
    if imc:
        return jsonify({'imc': imc, 'classificacao': classificacao})
    return jsonify({'error': 'Dados inválidos'}), 400

@app.route('/api/evolucao')
@login_required
def api_evolucao():
    """Retorna o histórico de IMC do usuário."""
    db = get_db()
    registros = db.execute(
        '''SELECT peso, imc, classificacao, data_registro FROM imc_records
           WHERE user_id = ? ORDER BY data_registro ASC''',
        (session['user_id'],)
    ).fetchall()
    
    return jsonify([dict(r) for r in registros])

@app.route('/api/limpar-chat', methods=['POST'])
@login_required
def limpar_chat():
    """Limpa o histórico de conversas do usuário."""
    db = get_db()
    db.execute('DELETE FROM conversations WHERE user_id = ?', (session['user_id'],))
    db.commit()
    return jsonify({'success': True})

# ----------------------------------------------------------
# Inicialização
# ----------------------------------------------------------

if __name__ == '__main__':
    # Inicializa o banco de dados se não existir
    if not os.path.exists(DATABASE):
        init_db()
    
    print("🥗 NutriChat iniciando...")
    print("📡 Acesse: http://localhost:5000")
    app.run(debug=True, port=5000)
