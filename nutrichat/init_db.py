#!/usr/bin/env python3
"""
NutriChat — init_db.py
Script para inicializar o banco de dados SQLite.
Execute este arquivo antes de rodar o app pela primeira vez.
"""
import os
import sqlite3

DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'nutrichat.db')
SCHEMA   = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')

def init():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    with open(SCHEMA, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"✅ Banco de dados criado em: {DATABASE}")

if __name__ == '__main__':
    init()
