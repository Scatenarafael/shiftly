# Clean Architecture — regras práticas

## Camadas
- Domain: entidades, value objects, serviços de domínio, exceções de negócio, interfaces/ports (quando fizer sentido).
- Application: use cases, DTOs, orchestrations, interfaces de gateways/repositories (ports).
- Infrastructure: SQLAlchemy models, repositories concretos, migrations, clients externos.
- Presentation: FastAPI routers, dependencies, schemas (Pydantic), exception handlers.

## “Cheiros” (não fazer)
- import FastAPI/SQLAlchemy/Pydantic dentro de domain
- use case chamando session.commit()
- router montando query SQLAlchemy
- infra retornando ORM model para presentation (sempre mapear para DTO)
