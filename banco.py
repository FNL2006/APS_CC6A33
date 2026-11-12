"""
banco.py - usa SQLite (do python) e guarda usuarios, encodings
e o log de todas as tentativas de acesso
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import numpy as np

import config


@contextmanager
def _conexao():
    config.DADOS_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def inicializar():
    with _conexao() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                nome  TEXT NOT NULL UNIQUE,
                cargo TEXT,
                nivel INTEGER NOT NULL CHECK (nivel IN (1, 2, 3))
            );
            CREATE TABLE IF NOT EXISTS encodings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id  INTEGER NOT NULL
                            REFERENCES usuarios(id) ON DELETE CASCADE,
                vetor       BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS acessos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora     TEXT NOT NULL,
                nome          TEXT NOT NULL,
                nivel_usuario INTEGER NOT NULL,
                nivel_porta   INTEGER NOT NULL,
                resultado     TEXT NOT NULL,
                motivo        TEXT
            );
            """
        )


def cadastrar_usuario(nome, cargo, nivel, encodings):
    """Grava o usuário + seus encodings e retorna o id."""
    if nivel not in config.NIVEIS:
        raise ValueError("Nível inválido.")
    if not encodings:
        raise ValueError("Não tem amostra de rosto para salvar.")
    try:
        with _conexao() as con:
            cur = con.execute(
                "INSERT INTO usuarios (nome, cargo, nivel) VALUES (?, ?, ?)",
                (nome, cargo, nivel),
            )
            uid = cur.lastrowid
            con.executemany(
                "INSERT INTO encodings (usuario_id, vetor) VALUES (?, ?)",
                [(uid, np.asarray(e, dtype=np.float64).tobytes()) for e in encodings],
            )
            return uid
    except sqlite3.IntegrityError:
        raise ValueError(f"Já existe um usuário chamado '{nome}'.")


def listar_usuarios():
    with _conexao() as con:
        return con.execute(
            "SELECT u.id, u.nome, u.cargo, u.nivel, COUNT(e.id) "
            "FROM usuarios u LEFT JOIN encodings e ON e.usuario_id = u.id "
            "GROUP BY u.id ORDER BY u.id"
        ).fetchall()


def remover_usuario(uid):
    with _conexao() as con:
        cur = con.execute("DELETE FROM usuarios WHERE id = ?", (uid,))
        return cur.rowcount > 0


def carregar_base():
    """Retorna (infos, matriz): infos[i] descreve a linha i da matriz de encodings."""
    with _conexao() as con:
        linhas = con.execute(
            "SELECT u.id, u.nome, u.nivel, e.vetor "
            "FROM usuarios u JOIN encodings e ON e.usuario_id = u.id"
        ).fetchall()

    infos = [{"id": linha[0], "nome": linha[1], "nivel": linha[2]} for linha in linhas]
    if linhas:
        matriz = np.array([np.frombuffer(linha[3], dtype=np.float64) for linha in linhas])
    else:
        matriz = np.empty((0, 128))
    return infos, matriz


def registrar_acesso(nome, nivel_usuario, nivel_porta, resultado, motivo=""):
    with _conexao() as con:
        con.execute(
            "INSERT INTO acessos (data_hora, nome, nivel_usuario, nivel_porta, resultado, motivo) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now().isoformat(sep=" ", timespec="seconds"),
             nome, nivel_usuario, nivel_porta, resultado, motivo),
        )


def listar_acessos():
    with _conexao() as con:
        return con.execute(
            "SELECT data_hora, nome, nivel_usuario, nivel_porta, resultado, motivo "
            "FROM acessos ORDER BY id"
        ).fetchall()

import sqlite3

def inicializar_tabela_arquivos():
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    cursor.execute("""
        create table if not exists arquivos (
            id integer primary key autoincrement,
            nome_arquivo text,
            caminho text,
            nivel_minimo integer,
            data_upload text
        )
    """)
    conn.commit()
    conn.close()

def salvar_arquivo_banco(nome, caminho, nivel):
    import datetime
    inicializar_tabela_arquivos()
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "insert into arquivos (nome_arquivo, caminho, nivel_minimo, data_upload) values (?, ?, ?, ?)",
        (nome, caminho, nivel, data_atual)
    )
    conn.commit()
    conn.close()

def listar_arquivos_por_nivel(nivel_usuario):
    inicializar_tabela_arquivos()
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    # Mostra apenas arquivos cujo nivel_minimo seja menor ou igual ao nível do utilizador logado
    cursor.execute(
        "select id, nome_arquivo, caminho, nivel_minimo, data_upload from arquivos where nivel_minimo <= ? order by id desc",
        (nivel_usuario,)
    )
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def remover_arquivo_banco(uid):
    inicializar_tabela_arquivos()
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    cursor.execute("delete from arquivos where id = ?", (uid,))
    conn.commit()
    conn.close()

def inicializar_tabela_logs():
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    cursor.execute("""
        create table if not exists logs_sistema (
            id integer primary key autoincrement,
            usuario text,
            acao text,
            detalhes text,
            data_hora text
        )
    """)
    conn.commit()
    conn.close()

def registrar_log(usuario, acao, detalhes):
    import datetime
    inicializar_tabela_logs()
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "insert into logs_sistema (usuario, acao, detalhes, data_hora) values (?, ?, ?, ?)",
        (usuario, acao, detalhes, data_atual)
    )
    conn.commit()
    conn.close()

def listar_logs():
    inicializar_tabela_logs()
    conn = sqlite3.connect("cofre.db")
    cursor = conn.cursor()
    cursor.execute("select id, usuario, acao, detalhes, data_hora from logs_sistema order by id desc")
    resultados = cursor.fetchall()
    conn.close()
    return resultados