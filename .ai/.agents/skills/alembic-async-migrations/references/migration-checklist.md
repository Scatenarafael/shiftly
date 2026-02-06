# Migration checklist

- [ ] upgrade() e downgrade() existem e são reversíveis quando possível
- [ ] índices e constraints revisados
- [ ] não há operações destrutivas sem plano (drop column/table) sem confirmação
- [ ] migration roda localmente e testes passam
