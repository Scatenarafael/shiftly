---
name: fastapi-clean-arch-api
description: Cria ou altera endpoints FastAPI seguindo Clean Architecture (schemas -> use case -> ports -> infra -> router) com mapeamento de erros e checklist de testes. Use quando o pedido envolver nova rota, alteração de contrato HTTP, ou nova regra de negócio exposta via API.
---

## Resultado esperado
- Router/controller fino (sem regra de negócio)
- Schemas Pydantic apenas na borda (presentation)
- Use case na camada application com DTOs simples
- Portas (interfaces/Protocols) definidas em domain/application
- Implementação infra (SQLAlchemy async) separada
- Testes: unit (use case) + integration (rota)

## Fluxo padrão (sempre)
1) Descobrir o padrão existente no repo:
   - encontre módulo/feature semelhante
   - copie a estrutura
2) Definir contrato HTTP:
   - path, method, status codes
   - request/response schemas
   - erros de negócio e seus status codes
3) Implementar de dentro pra fora:
   a) Domain: entidades/VOs/exceções (se necessário)
   b) Application: DTOs + use case + portas
   c) Infrastructure: repos/clients concretos
   d) Presentation: router + schemas + DI
4) Testes:
   - unit test do use case cobrindo regras e exceções
   - integration test da rota cobrindo 1 happy + 1 erro
5) Rodar suíte e corrigir

## Regras obrigatórias
- Domain NÃO importa FastAPI, Pydantic, SQLAlchemy.
- Router NÃO contém if/else de regra de negócio; só chama use case.
- Não retornar model SQLAlchemy direto no response.
- Não misturar transação/commit no use case.

## Templates (copie e adapte)
Use os templates em:
- assets/templates/router.py.tpl
- assets/templates/schemas.py.tpl
- assets/templates/use_case.py.tpl
- assets/templates/repo_port.py.tpl
- assets/templates/repo_sqlalchemy.py.tpl

Substitua marcadores:
{{module}}, {{entity}}, {{Entity}}, {{id_type}} etc.

## Referências internas
- references/clean-architecture.md
- references/feature-flow.md
