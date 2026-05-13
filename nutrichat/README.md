# 🥗 NutriChat — Chatbot Nutricional Inteligente

Sistema web completo de chatbot nutricional com inteligência artificial (Claude/Anthropic), Flask, SQLite e interface moderna.

---

## 📋 Funcionalidades

- ✅ Login e cadastro de usuários com autenticação segura
- ✅ Chatbot IA com a API Claude (Anthropic) — respostas personalizadas
- ✅ Cálculo de IMC com barra visual e classificação
- ✅ Sugestão de dietas conforme objetivo (emagrecer, ganhar massa, manter peso)
- ✅ Histórico completo de conversas no banco de dados
- ✅ Perfil nutricional editável (peso, altura, idade, nível de atividade)
- ✅ Evolução do peso registrada automaticamente
- ✅ Interface estilo ChatGPT, responsiva para celular e desktop
- ✅ Chips de sugestão rápida para perguntas frequentes

---

## 🗂 Estrutura do Projeto

```
nutrichat/
├── app.py                  # Aplicação Flask principal
├── init_db.py              # Script de inicialização do banco
├── requirements.txt        # Dependências Python
├── .env.example            # Modelo de variáveis de ambiente
├── templates/
│   ├── login.html          # Tela de login
│   ├── cadastro.html       # Tela de cadastro
│   └── chat.html           # Interface principal do chat
├── static/
│   ├── css/
│   │   ├── main.css        # Estilos globais e autenticação
│   │   └── chat.css        # Estilos do chat
│   └── js/
│       └── chat.js         # Lógica do frontend
└── database/
    ├── schema.sql          # Script SQL do banco de dados
    └── nutrichat.db        # Banco SQLite (gerado automaticamente)
```

---

## ⚙️ Instalação e Configuração

### Pré-requisitos
- Python 3.9 ou superior
- pip
- Conta na Anthropic (para obter a chave de API)

### Passo 1 — Clone ou extraia o projeto
```bash
cd nutrichat
```

### Passo 2 — Crie e ative um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Passo 3 — Instale as dependências
```bash
pip install -r requirements.txt
```

### Passo 4 — Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione:
# - SECRET_KEY: qualquer string aleatória longa
# - ANTHROPIC_API_KEY: sua chave da API Anthropic
```

**Obter chave Anthropic:**
1. Acesse https://console.anthropic.com/
2. Crie uma conta ou faça login
3. Vá em "API Keys" e gere uma nova chave
4. Cole no arquivo `.env`

### Passo 5 — Inicialize o banco de dados
```bash
python init_db.py
```

### Passo 6 — Execute o servidor
```bash
python app.py
```

### Passo 7 — Acesse no navegador
```
http://localhost:5000
```

---

## 🔑 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|---|---|---|
| `SECRET_KEY` | Chave secreta para sessões Flask | `minha-chave-super-secreta-123` |
| `ANTHROPIC_API_KEY` | Chave de API da Anthropic (Claude) | `sk-ant-api03-...` |

---

## 🧪 Como Usar

1. **Cadastro**: Crie sua conta informando nome, e-mail, senha e dados corporais (opcional na hora do cadastro, pode editar depois).

2. **Login**: Entre com seu e-mail e senha.

3. **Chat**: Converse com a NutriBot! Exemplos de perguntas:
   - "Qual seria uma dieta ideal para eu emagrecer?"
   - "Calcule meu IMC e me explique"
   - "Sugira um cardápio semanal saudável"
   - "Quais alimentos são ricos em proteína?"
   - "Quantas calorias devo consumir por dia?"

4. **Editar Perfil**: Clique no ícone de usuário ou no botão "Editar perfil" na sidebar para atualizar peso, altura e objetivo.

5. **Chips rápidos**: Use os botões de atalho na sidebar para perguntas frequentes.

---

## 🛠 Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Backend | Python 3, Flask 3 |
| Banco de Dados | SQLite (via Flask nativo) |
| IA | Anthropic Claude (claude-opus-4-5) |
| Fontes | Cabinet Grotesk, DM Sans (Google Fonts) |

---

## 📦 Dependências (requirements.txt)

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Bcrypt==1.0.1
anthropic==0.40.0
python-dotenv==1.0.1
Werkzeug==3.0.4
```

---

## 🔒 Segurança

- Senhas armazenadas como hash SHA-256
- Sessões protegidas com `SECRET_KEY`
- Proteção contra injeção SQL via queries parametrizadas
- Rotas protegidas com decorator `@login_required`

---

## 🤝 Contribuição

Sinta-se à vontade para abrir issues ou pull requests com melhorias!

---

## 📄 Licença

MIT License — uso livre para fins educacionais e comerciais.
