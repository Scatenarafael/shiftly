# Fluxo de feature (API)

1) Router recebe request -> valida com Schema (Pydantic)
2) Router transforma para InputDTO e chama UseCase.execute(dto)
3) Use case aplica regra (domain) e usa Port(s) para IO
4) Infra implementa IO (repo/client)
5) Use case retorna OutputDTO
6) Router serializa OutputDTO via Schema e responde

## Erros
- domain/application levantam exceções tipadas
- presentation captura e converte em HTTPException / handlers
