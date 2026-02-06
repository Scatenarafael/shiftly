# SQLAlchemy async — guias rápidos

## Exists
- select(pk).where(...).limit(1) é suficiente

## Create
- session.add(obj)
- await session.flush()
- retorne obj/record
- commit no UoW / camada de transação por request

## Update
- carregue com select + scalar_one()
- aplique mudanças
- flush
