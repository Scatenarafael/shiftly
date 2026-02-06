# Testing Strategy

## Unit
- Não importa FastAPI.
- Não acessa DB real.
- Porta mockada.

## Integration
- Usa httpx AsyncClient.
- Testa status code, shape do JSON e erro mapeado.
- Evitar testar SQLAlchemy profundamente aqui (isso vira teste de infra).
