# Contribuindo

Contribuições são bem-vindas. Antes de começar uma alteração maior, abra uma issue descrevendo o problema, a solução proposta e os impactos esperados.

## Ambiente local

Siga o guia de instalação do [README](README.md). Crie uma branch a partir da branch principal e mantenha cada pull request focado em uma única mudança.

## Verificações obrigatórias

Execute antes de abrir o pull request:

```bash
make lint
make test
cd frontend && pnpm format
```

Alterações de comportamento devem incluir testes. Migrações de banco precisam ser compatíveis com instalações que já possuem dados locais.

## Pull requests

Na descrição, informe:

- o problema resolvido
- as principais decisões técnicas
- como a alteração foi validada
- capturas de tela para mudanças visuais

Ao contribuir, você concorda que sua alteração será distribuída sob a licença MIT do projeto.
