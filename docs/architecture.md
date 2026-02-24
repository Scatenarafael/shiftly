# Arquitetura do Projeto

## Visao geral
Este projeto segue Clean Architecture com FastAPI, mantendo as dependencias apontando para dentro. A regra principal e separar regras de negocio, casos de uso e implementacoes de infraestrutura (DB, auth, etc), deixando a camada HTTP como adaptador.

## Camadas e responsabilidades
- Domain (`src/domain`): entidades e erros de negocio. Nao depende de FastAPI, SQLAlchemy, Pydantic ou infra.
- Application/Use cases (`src/usecases`): casos de uso que orquestram regras e portas. Retornam DTOs simples.
- Interfaces/Ports (`src/interfaces`): contratos de repositorios e servicos (ex: token), alem de DTOs de transporte.
- Infrastructure (`src/infra`): implementacoes concretas (repositorios SQLAlchemy async, modelos DB, servicos JWT, settings).
- Presentation (`src/app/controllers`): routers FastAPI, schemas Pydantic e mapeamento de erros para HTTP.

## Fluxo tipico de requisicao
1. Router valida input com Pydantic (`src/app/controllers/schemas/pydantic`).
2. Router instancia o use case via DI (`src/app/dependencies.py`).
3. Use case chama a porta (interface) definida em `src/interfaces`.
4. Implementacao infra executa a operacao (SQLAlchemy async) e devolve entidades de dominio.
5. Use case mapeia para DTO e o router serializa a resposta.

## Mapa rapido do codigo
- `main.py`: entrada da aplicacao; registra middleware, DI e routers.
- `src/domain/entities`: entidades puras de negocio (ex: User, Company, Role).
- `src/domain/errors.py`: excecoes de negocio usadas pelos use cases.
- `src/usecases`: casos de uso por agregados (users, companies, roles, workdays, auth).
- `src/interfaces`: contratos (repositorios/servicos) e DTOs de transporte.
- `src/infra/db/models`: modelos SQLAlchemy.
- `src/infra/repositories`: adaptadores SQLAlchemy para as portas.
- `src/infra/services`: servicos como JWT.
- `src/infra/settings`: config, logging e conexao DB.
- `src/app/controllers`: routers FastAPI e schemas Pydantic.
- `tests`: unit e integration tests.

## Injecao de dependencias
- `src/app/dependencies.py` declara as portas como dependencias abstratas.
- `main.py` faz o override apontando para implementacoes infra (ex: `UsersRepository`).
- Cada request recebe uma `AsyncSession` via `get_db_session()`.

## Persistencia e transacoes
- Repositorios infra usam SQLAlchemy AsyncSession (`src/infra/repositories`).
- Commit/rollback ficam na camada infra, nao no dominio.
- Modelos DB vivem em `src/infra/db/models` e migrations em `alembic/`.

## Autenticacao
- `AuthService` (`src/usecases/auth_service.py`) concentra regras de login, refresh e logout.
- `AuthMiddleware` valida token de acesso e protege rotas privadas.
- Tokens e refresh sao tratados via `ITokenService` e `IJWTRepository`.

## Erros e mapeamento HTTP
- Excecoes de negocio ficam em `src/domain/errors.py`.
- Routers capturam excecoes e convertem para status HTTP apropriados.

## Testes
- Unit tests de casos de uso: `tests/unit`.
- Integration tests de repos e APIs: `tests/integration` e `tests/api`.

## Como adicionar uma nova feature (resumo)
1. Definir/ajustar entidades ou erros no dominio.
2. Criar use case em `src/usecases`.
3. Ajustar porta em `src/interfaces` se necessario.
4. Implementar repositorio/servico em `src/infra`.
5. Expor rota em `src/app/controllers` com schemas Pydantic.
6. Adicionar testes unit e integration.
