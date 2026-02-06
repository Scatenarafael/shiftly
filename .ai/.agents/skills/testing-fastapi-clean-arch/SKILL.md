---
name: testing-fastapi-clean-arch
description: Escreve testes para APIs FastAPI em Clean Architecture: unit tests de use cases (sem FastAPI/DB real quando possível) e integration tests de routers (httpx AsyncClient). Use quando criar/alterar endpoints, casos de uso, regras de negócio, ou mapeamento de erros.
---

## Estratégia obrigatória
- Unit (rápido): testa use case e regras com doubles/mocks das portas.
- Integration (mínimo): testa contrato HTTP e mapeamento de erros.

## Unit test — padrão
- Given/When/Then
- mock da porta (repo) com comportamento explícito
- validar:
  - retorno correto (DTO)
  - exceções corretas (DomainError)

## Integration test — padrão
- instancia app
- injeta overrides de dependências (use case/repo) quando possível
- 1 happy path + 1 erro de negócio

## Scripts
- scripts/run_tests.sh
## Referência
- references/testing-strategy.md
