from flask import Flask, render_template_string, request, redirect, url_for
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "atividades_web.db")

CATEGORIES = ["Universidade", "Casa", "Estudo", "Trabalho", "Pessoal"]
PRIORITIES = ["Alta", "Média", "Baixa"]
STATUS = ["Pendente", "Em progresso", "Concluída"]

HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#111827">
    <title>Gestor de Atividades Mobile</title>
    <style>
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f3f4f6;
            color: #111827;
        }
        header {
            background: linear-gradient(135deg, #111827, #2563eb);
            color: white;
            padding: 18px 16px 22px;
            border-bottom-left-radius: 22px;
            border-bottom-right-radius: 22px;
            box-shadow: 0 4px 16px rgba(0,0,0,.15);
        }
        header h1 {
            margin: 0;
            font-size: 22px;
        }
        header p {
            margin: 6px 0 0;
            font-size: 14px;
            opacity: .92;
        }
        .container {
            max-width: 760px;
            margin: 0 auto;
            padding: 14px;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: -18px;
            margin-bottom: 14px;
        }
        .card {
            background: white;
            border-radius: 18px;
            padding: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,.08);
        }
        .card h3 {
            margin: 0 0 8px;
            font-size: 12px;
            color: #6b7280;
        }
        .card p {
            margin: 0;
            font-size: 20px;
            font-weight: bold;
        }
        .panel {
            background: white;
            border-radius: 18px;
            padding: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,.08);
            margin-bottom: 14px;
        }
        h2 {
            margin: 0 0 12px;
            font-size: 18px;
        }
        label {
            display: block;
            margin: 10px 0 6px;
            font-weight: bold;
            font-size: 14px;
        }
        input, select {
            width: 100%;
            padding: 13px 12px;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            font-size: 16px;
            background: #fff;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 13px 14px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            text-decoration: none;
            font-size: 15px;
            font-weight: bold;
        }
        .btn-primary { background: #2563eb; color: white; }
        .btn-success { background: #16a34a; color: white; }
        .btn-warning { background: #f59e0b; color: white; }
        .btn-danger { background: #dc2626; color: white; }
        .btn-gray { background: #6b7280; color: white; }
        .stack { display: grid; gap: 8px; }
        .task {
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 12px;
            margin-bottom: 10px;
            background: #fff;
        }
        .task-top {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        .task-title {
            font-weight: bold;
            font-size: 16px;
        }
        .muted {
            color: #6b7280;
            font-size: 13px;
        }
        .meta {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin: 10px 0;
        }
        .meta div {
            background: #f9fafb;
            border-radius: 12px;
            padding: 9px;
            font-size: 13px;
        }
        .badge {
            padding: 5px 9px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }
        .alta { background: #fee2e2; color: #b91c1c; }
        .media { background: #fef3c7; color: #92400e; }
        .baixa { background: #dcfce7; color: #166534; }
        .pending { background: #e5e7eb; color: #374151; }
        .progress { background: #dbeafe; color: #1d4ed8; }
        .done { background: #dcfce7; color: #166534; }
        .actions {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 10px;
        }
        .filter-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 8px;
        }
        .hint {
            margin-top: 10px;
            background: #eff6ff;
            color: #1d4ed8;
            border-radius: 12px;
            padding: 10px;
            font-size: 13px;
        }
        @media (min-width: 761px) {
            .desktop-grid {
                display: grid;
                grid-template-columns: 1fr 1.25fr;
                gap: 14px;
            }
            .cards { grid-template-columns: repeat(5, 1fr); }
            .actions { grid-template-columns: repeat(5, 1fr); }
        }
    </style>
</head>
<body>
    <header>
        <h1>Gestor de Atividades</h1>
        <p>Versão pronta para celular</p>
    </header>

    <div class="container">
        <div class="cards">
            <div class="card"><h3>Total</h3><p>{{ stats.total }}</p></div>
            <div class="card"><h3>Pendentes</h3><p>{{ stats.pendentes }}</p></div>
            <div class="card"><h3>Concluídas</h3><p>{{ stats.concluidas }}</p></div>
            <div class="card"><h3>Restantes</h3><p>{{ stats.minutos_restantes }} min</p></div>
            <div class="card"><h3>Tempo real</h3><p>{{ stats.tempo_real }}</p></div>
        </div>

        <div class="desktop-grid">
            <div class="panel">
                <h2>Nova atividade</h2>
                <form method="post" action="/add">
                    <label>Título</label>
                    <input type="text" name="titulo" required>

                    <label>Categoria</label>
                    <select name="categoria" required>
                        {% for c in categories %}
                        <option value="{{ c }}">{{ c }}</option>
                        {% endfor %}
                    </select>

                    <label>Prioridade</label>
                    <select name="prioridade" required>
                        {% for p in priorities %}
                        <option value="{{ p }}">{{ p }}</option>
                        {% endfor %}
                    </select>

                    <label>Tempo estimado (minutos)</label>
                    <input type="number" name="tempo_estimado" min="1" required>

                    <label>Tempo realizado agora (minutos)</label>
                    <input type="number" name="tempo_real" min="0" value="0" required>

                    <label>Data limite</label>
                    <input type="date" name="data_limite">

                    <br>
                    <button class="btn btn-primary" type="submit">Adicionar atividade</button>
                </form>
                <div class="hint">No iPhone, abre no Safari e usa “Adicionar ao ecrã principal”.</div>
            </div>

            <div class="panel">
                <h2>Atividades</h2>
                <form method="get" action="/">
                    <div class="filter-grid">
                        <select name="categoria">
                            <option value="Todas">Todas</option>
                            {% for c in categories %}
                            <option value="{{ c }}" {% if filtro_categoria == c %}selected{% endif %}>{{ c }}</option>
                            {% endfor %}
                        </select>
                        <select name="estado">
                            <option value="Todos">Todos</option>
                            {% for s in status_list %}
                            <option value="{{ s }}" {% if filtro_estado == s %}selected{% endif %}>{{ s }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button class="btn btn-gray" type="submit">Aplicar filtros</button>
                </form>

                <div style="margin-top:12px;">
                    {% for t in tarefas %}
                    <div class="task">
                        <div class="task-top">
                            <div>
                                <div class="task-title">{{ t['titulo'] }}</div>
                                <div class="muted">{{ t['categoria'] }}</div>
                            </div>
                            <div>
                                <span class="badge {% if t['estado']=='Pendente' %}pending{% elif t['estado']=='Em progresso' %}progress{% else %}done{% endif %}">{{ t['estado'] }}</span>
                            </div>
                        </div>

                        <div>
                            <span class="badge {% if t['prioridade']=='Alta' %}alta{% elif t['prioridade']=='Média' %}media{% else %}baixa{% endif %}">{{ t['prioridade'] }}</span>
                        </div>

                        <div class="meta">
                            <div><strong>Estimado</strong><br>{{ t['tempo_estimado'] }} min</div>
                            <div><strong>Real</strong><br>{{ format_minutes(t['tempo_real']) }}</div>
                            <div><strong>Limite</strong><br>{{ t['data_limite'] or '-' }}</div>
                            <div><strong>ID</strong><br>{{ t['id'] }}</div>
                        </div>

                        <div class="actions">
                            <a class="btn btn-warning" href="/status/{{ t['id'] }}/Em%20progresso">Progresso</a>
                            <a class="btn btn-success" href="/status/{{ t['id'] }}/Concluída">Concluir</a>
                            <a class="btn btn-gray" href="/status/{{ t['id'] }}/Pendente">Pendente</a>
                            <a class="btn btn-primary" href="/time/{{ t['id'] }}">+ Tempo</a>
                            <a class="btn btn-danger" href="/delete/{{ t['id'] }}" onclick="return confirm('Eliminar esta atividade?')">Eliminar</a>
                        </div>
                    </div>
                    {% else %}
                    <div class="task">Nenhuma atividade encontrada.</div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

TIME_HTML = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adicionar tempo</title>
    <style>
        body { font-family: Arial, sans-serif; background:#f4f6f8; padding:20px; }
        .box { max-width:500px; margin:auto; background:white; border-radius:14px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.08); }
        input { width:100%; padding:11px; border:1px solid #ccc; border-radius:10px; }
        .btn { padding:10px 14px; border:none; border-radius:10px; cursor:pointer; text-decoration:none; }
        .btn-primary { background:#2563eb; color:white; }
        .btn-gray { background:#6b7280; color:white; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Adicionar tempo realizado</h2>
        <p><strong>Atividade:</strong> {{ tarefa['titulo'] }}</p>
        <p><strong>Tempo atual:</strong> {{ format_minutes(tarefa['tempo_real']) }}</p>
        <form method="post">
            <label>Minutos a adicionar</label><br><br>
            <input type="number" name="minutos" min="1" required>
            <br><br>
            <button class="btn btn-primary" type="submit">Guardar</button>
            <a class="btn btn-gray" href="/">Voltar</a>
        </form>
    </div>
</body>
</html>
"""


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            tempo_estimado INTEGER NOT NULL,
            tempo_real INTEGER NOT NULL DEFAULT 0,
            data_limite TEXT,
            estado TEXT NOT NULL DEFAULT 'Pendente',
            criado_em TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def format_minutes(total_minutes):
    h = int(total_minutes) // 60
    m = int(total_minutes) % 60
    return f"{h:02}h {m:02}m"


def get_stats():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tarefas")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tarefas WHERE estado='Pendente'")
    pendentes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tarefas WHERE estado='Concluída'")
    concluidas = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(tempo_estimado),0) FROM tarefas WHERE estado!='Concluída'")
    minutos_restantes = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(tempo_real),0) FROM tarefas")
    tempo_real = cur.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "pendentes": pendentes,
        "concluidas": concluidas,
        "minutos_restantes": minutos_restantes,
        "tempo_real": format_minutes(tempo_real),
    }


@app.route("/")
def index():
    filtro_categoria = request.args.get("categoria", "Todas")
    filtro_estado = request.args.get("estado", "Todos")

    conn = connect_db()
    cur = conn.cursor()
    query = "SELECT * FROM tarefas WHERE 1=1"
    params = []

    if filtro_categoria != "Todas":
        query += " AND categoria=?"
        params.append(filtro_categoria)
    if filtro_estado != "Todos":
        query += " AND estado=?"
        params.append(filtro_estado)

    query += " ORDER BY CASE prioridade WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 ELSE 3 END, id DESC"
    cur.execute(query, params)
    tarefas = cur.fetchall()
    conn.close()

    return render_template_string(
        HTML,
        tarefas=tarefas,
        categories=CATEGORIES,
        priorities=PRIORITIES,
        status_list=STATUS,
        stats=get_stats(),
        filtro_categoria=filtro_categoria,
        filtro_estado=filtro_estado,
        format_minutes=format_minutes,
    )


@app.route("/add", methods=["POST"])
def add_task():
    titulo = request.form.get("titulo", "").strip()
    categoria = request.form.get("categoria", "").strip()
    prioridade = request.form.get("prioridade", "").strip()
    tempo_estimado = request.form.get("tempo_estimado", "0").strip()
    tempo_real = request.form.get("tempo_real", "0").strip()
    data_limite = request.form.get("data_limite", "").strip()

    if not titulo:
        return redirect(url_for("index"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO tarefas (titulo, categoria, prioridade, tempo_estimado, tempo_real, data_limite, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            titulo,
            categoria,
            prioridade,
            int(tempo_estimado),
            int(tempo_real),
            data_limite if data_limite else None,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/status/<int:task_id>/<status>")
def change_status(task_id, status):
    if status not in STATUS:
        return redirect(url_for("index"))
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE tarefas SET estado=? WHERE id=?", (status, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tarefas WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/time/<int:task_id>", methods=["GET", "POST"])
def add_time(task_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tarefas WHERE id=?", (task_id,))
    tarefa = cur.fetchone()

    if tarefa is None:
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        minutos = int(request.form.get("minutos", "0"))
        cur.execute("UPDATE tarefas SET tempo_real = tempo_real + ? WHERE id=?", (minutos, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn.close()
    return render_template_string(TIME_HTML, tarefa=tarefa, format_minutes=format_minutes)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
