# ADR 005: Matrícula como vínculo acadêmico

## Decisão

Aluno e turma permanecem entidades separadas. A tabela `matricula` representa o vínculo do aluno com uma turma em um ano letivo e mantém histórico de transferência e encerramento.

Uma matrícula ativa por aluno e ano letivo é garantida por índice único parcial. Transferência encerra a matrícula atual e cria outra na turma de destino. Encerramento exige motivo.

O frontend expõe um fluxo inicial de secretaria para cadastrar aluno e matriculá-lo em uma das turmas seed. A API continua sendo a fonte das regras e validações.

## Alternativas descartadas

- `turma_id` diretamente em `aluno`: perderia histórico e impediria transferências.
- Exclusão física do vínculo: removeria informação necessária para auditoria acadêmica.
- Permitir múltiplas matrículas ativas no mesmo ano: geraria frequência ambígua.
