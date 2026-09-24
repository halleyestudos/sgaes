# ADR 003: Frequência idempotente e alerta transacional

## Decisão

A chamada é persistida em `sga.frequencia` com unicidade por turma, aluno, data e ordem. O endpoint faz upsert lógico e recalcula o alerta de cada aluno na mesma transação.

Os níveis são `RISCO_ABANDONO` abaixo de 75% e `LIMITE_LEGAL_30` abaixo de 30%. O percentual mínimo de 75% permanece explícito no serviço para ser parametrizado por rede em uma próxima migração.

## Alternativas descartadas

- Inserção sem unicidade: permitiria duplicidade ao reenviar uma chamada.
- Cálculo assíncrono posterior: abriria uma janela em que o painel mostraria frequência sem o alerta correspondente.
- Regra no router: dificultaria testes e reutilização; a regra fica em `services/alerta_service.py`.
