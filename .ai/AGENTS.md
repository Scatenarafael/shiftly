# Codex Project Instructions — FastAPI + Clean Architecture (Python)

## Objetivo (sempre)
Construir e manter APIs em FastAPI seguindo Clean Architecture:
- Domain: regras de negócio puras (sem FastAPI, sem SQLAlchemy).
- Application: casos de uso (orquestra a regra e portas).
- Infrastructure: implementação de portas (DB, HTTP clients, brokers).
- Presentation/Interface: FastAPI routers/controllers/schemas e DI.

## Regras de arquitetura (não-negociáveis)
1) Dependências sempre apontam para dentro:
   presentation -> application -> domain
   infrastructure -> application/domain (implementa portas), mas domain não importa infra.
2) Domain não importa frameworks (FastAPI, SQLAlchemy, Pydantic, httpx, etc).
3) Use cases NÃO recebem Request/Response; recebem DTOs simples.
4) Repositórios:
   - Domain/Application define PORTAS (interfaces/Protocols).
   - Infrastructure implementa com SQLAlchemy AsyncSession (ou outro adaptador).
5) Erros:
   - Domain define exceções de negócio.
   - Presentation mapeia exceções para HTTP status codes.
6) Um “endpoint” é só um adaptador: valida input (schema), chama use case, retorna output (schema).

## Padrão de entrega para qualquer mudança em API
- Ajustar/Adicionar: schema(s) (input/output)
- Ajustar/Adicionar: use case
- Ajustar/Adicionar: porta(s) (repo/clients) se necessário
- Ajustar/Adicionar: implementação infra (SQLAlchemy, etc)
- Ajustar/Adicionar: rota FastAPI (router)
- Testes:
  - unit test do use case (regra/fluxo)
  - integration test da rota (happy + 1 erro relevante)

## Convenções (python)
- type hints obrigatórios
- funções pequenas; sem lógica de negócio em routers
- prefira retornar Result/DTOs em application; serialize na borda
- não adicionar dependência nova sem pedir confirmação explícita

## Banco e transações
- Uma AsyncSession por request (dependency injection).
- Commits/rollbacks são responsabilidade da camada infra (ou UoW), não do domain.
- Evite N+1 (prefetch/selectinload quando fizer sentido).

## Skills (use sempre que aplicável)
Para implementar features de API, use estas skills:
- $fastapi-clean-arch-api : criar/alterar endpoint+use case no padrão
- $sqlalchemy-async-repository-pattern : criar/alterar repos SQLAlchemy async
- $testing-fastapi-clean-arch : escrever testes unit/integration no padrão
- $alembic-async-migrations : criar/revisar migrations com checklist

## Como trabalhar
- Antes de codar: proponha um plano curto e um checklist de “done”.
- Depois de codar: rode testes e conserte falhas.
- Se faltar contexto: procure no repo por padrões existentes e replique.

