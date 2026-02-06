---
name: alembic-async-migrations
description: Cria e revisa migrations Alembic para projetos com SQLAlchemy async, garantindo upgrade/downgrade seguros, revisão de autogenerate e alinhamento com models. Use quando adicionar/alterar tabelas, colunas, índices, constraints, ou ajustar schema.
---

## Fluxo
1) Verificar alteração necessária (models e/ou SQL).
2) Gerar revision (autogenerate se existir no projeto).
3) Revisar a migration:
   - nomes claros
   - índices/constraints
   - downgrade funcional
4) Rodar migration + testes.

## Checklist
- references/migration-checklist.md
