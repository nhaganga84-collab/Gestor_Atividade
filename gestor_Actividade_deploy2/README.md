# Gestor_Actividade

Projeto Flask preparado para deploy no Render.

## Ficheiros principais
- `app.py` -> aplicação principal
- `atividades_web.db` -> base de dados SQLite
- `requirements.txt` -> dependências
- `Procfile` -> comando de arranque
- `render.yaml` -> configuração opcional do Render

## Testar localmente
```bash
pip install -r requirements.txt
python app.py
```

## Deploy no Render
1. Criar repositório no GitHub.
2. Enviar estes ficheiros para o repositório.
3. Entrar no Render.
4. New + -> Web Service.
5. Ligar ao GitHub.
6. Escolher o repositório.
7. Confirmar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
8. Fazer Deploy.

## Nota importante
A base de dados SQLite funciona para testes e projetos pequenos. Em deploy, os dados podem não ser permanentes em alguns planos/serviços. Para uso mais profissional, o ideal é migrar depois para PostgreSQL.
