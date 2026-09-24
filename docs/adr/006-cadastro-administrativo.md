# ADR 006: Cadastro administrativo completo no frontend

## Decisão

A secretaria precisa criar escola, ano letivo, turma, aluno e matrícula pela interface, sem depender do seed ou do `/docs`.

O cliente HTTP passou a traduzir erros 422/409 e falhas de rede em mensagens em português. O proxy do Vite usa `127.0.0.1:8000` no Windows nativo e, no WSL, o IP do host Windows obtido pela rota padrão. O backend precisa escutar em `0.0.0.0:8000` para essa ponte funcionar.

Os testes de cadastro deixaram de depender de `escola_id=1` e `turma_id=1`. Cada caso cria a estrutura necessária e cobre matrícula duplicada, vínculo inválido e inativação lógica.

## Alternativas descartadas

- Manter criação só na API: a tela de cadastros parecia quebrada mesmo com o backend saudável.
- Continuar com `host.docker.internal` como padrão: neste ambiente o endereço não alcança o Uvicorn no Windows; a rota padrão do WSL funciona.
- Apagar registros em vez de inativar: perderia histórico acadêmico.
