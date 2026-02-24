# Shiftly API

## Documentacao
- Arquitetura: `docs/architecture.md`

## Rodando testes do zero
### 1) Pre-requisitos
- Python `3.13+`
- `uv` instalado
- Docker + Docker Compose

### 2) Instalar dependencias do projeto
```bash
uv sync --dev
```

### 3) Subir o Postgres local
```bash
docker compose up -d db
```

Opcional: validar se o banco ficou pronto.
```bash
docker exec postgres_container pg_isready -U postgres -d shiftly_db
```

### 4) Garantir que o banco de teste existe
```bash
docker exec postgres_container psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'shiftly_test'" | grep -q 1 || \
docker exec postgres_container psql -U postgres -c "CREATE DATABASE shiftly_test;"
```

### 5) Rodar a bateria completa de testes
```bash
PYTHONPATH=. TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_test uv run pytest -q
```

Ou com o script Python da raiz do projeto:
```bash
uv run python run_tests.py
```

Por padrao, essa execucao grava o andamento completo dos testes em:
- `src/logs/tests.log`

### Bootstrap de migrations (automatico)
- Ao iniciar a suite, o `tests/conftest.py` compara a revisão atual do banco de teste com o `head` do Alembic.
- Se estiver desatualizado (ou sem `alembic_version`), executa `alembic upgrade head` automaticamente.
- Se existir schema legado sem versionamento, o bootstrap reseta `public` e reaplica as migrations.

### Comandos por camada (opcional)
```bash
PYTHONPATH=. TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_test uv run pytest tests/unit -q
PYTHONPATH=. TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/shiftly_test uv run pytest tests/integration tests/api -q
```

### Rodar contra outro banco de testes
Se voce nao usar Docker local, basta apontar `TEST_DATABASE_URL` para um Postgres acessivel:
```bash
PYTHONPATH=. TEST_DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db_test> uv run pytest -q
```

Com log customizado no script:
```bash
uv run python run_tests.py --log-file src/logs/meu_log_testes.log
```

### Troubleshooting rapido
- `database "shiftly_test" does not exist`:
  execute o passo 4.
- `password authentication failed for user`:
  valide usuario/senha do `TEST_DATABASE_URL` e do container Postgres.
- Ambiente de testes muito sujo e voce quer resetar somente o schema do banco de teste:
```bash
docker exec postgres_container psql -U postgres -d shiftly_test -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```
