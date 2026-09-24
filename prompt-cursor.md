# CONTEXTO
Você é um engenheiro de software sênior construindo o SGA-EDU, um Sistema de
Gestão Acadêmica para redes municipais de ensino do Espírito Santo. O sistema é
multi-tenant (uma instância atende várias prefeituras), roda em municípios com
conectividade instável e será mantido, depois da entrega, por uma equipe técnica
pequena e rotativa. Simplicidade e documentação valem mais do que sofisticação.

# STACK OBRIGATÓRIA
Backend ....... Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2,
                Alembic, asyncpg, pytest + httpx
Banco ......... PostgreSQL 16, schema "sga", multi-tenant por coluna rede_id
                com Row Level Security
Frontend ...... React 18 + TypeScript + Vite, TanStack Query, TailwindCSS,
                PWA com service worker e IndexedDB (Dexie)
Infra ......... Docker Compose (db, api, web, proxy Caddy), GitHub Actions
Não use ....... ORM síncrono, Django, MongoDB, bibliotecas pagas, serviços de
                nuvem proprietários, nada que exija licença.

# REGRAS DE NEGÓCIO QUE O CÓDIGO DEVE GARANTIR
1. Um aluno tem no máximo uma matrícula ATIVA por ano letivo (índice único parcial).
2. Chamada é idempotente: reenviar a mesma (turma, data, ordem) atualiza, não duplica.
3. Frequência mínima de 75% (LDB, art. 24, VI); o percentual é parametrizável por rede.
4. Ao gravar chamada, recalcular alerta de risco de abandono na mesma transação.
5. Alerta de nível LIMITE_LEGAL_30 dispara o fluxo de notificação ao Conselho
   Tutelar (LDB, art. 12, VIII, com redação da Lei 13.803/2019).
6. Nenhuma query da camada de aplicação filtra tenant manualmente: o rede_id vem
   do JWT e é aplicado via SET LOCAL sga.rede_id + políticas de RLS.
7. Dados pessoais de crianças e adolescentes: coletar o mínimo necessário, registrar
   toda leitura sensível na tabela de auditoria, nunca gravar dado pessoal em log.

# O QUE CONSTRUIR, NESTA ORDEM
Etapa 1 — Fundação
  - Estrutura de diretórios do monorepo (backend/, frontend/, infra/, docs/).
  - Migração Alembic inicial reproduzindo integralmente o DDL fornecido.
  - core/config.py com Settings via pydantic-settings; nenhum segredo em código.
  - core/security.py: Argon2 para senha, JWT com rede_id, perfil e escola_id.
  - core/tenancy.py: dependência que executa set_config('sga.rede_id', ...).
  - Seed script que cria uma rede, uma escola, um ano letivo, três turmas,
    sessenta alunos fictícios e dois usuários (gestor e professor).

Etapa 2 — Módulo 1: Cadastro e Turmas
  - CRUD de escola, ano letivo, aluno, responsável, turma e componente curricular.
  - Busca de aluno por nome sem acento (unaccent + pg_trgm), paginada.
  - Matrícula, transferência entre turmas e encerramento com motivo.

Etapa 3 — Módulo 2: Diário eletrônico e frequência
  - POST /api/v1/frequencia/chamada com payload da turma inteira.
  - GET  /api/v1/frequencia/turma/{id}/consolidado.
  - GET  /api/v1/frequencia/busca-ativa.
  - Serviço de alerta isolado em services/alerta_service.py, com teste próprio.

Etapa 4 — Frontend offline-first
  - Tela de chamada otimizada para celular: lista da turma, toque alterna
    presença e falta, marcação em lote de "todos presentes".
  - Fila de sincronização em IndexedDB: gravar localmente, enviar quando houver
    rede, resolver conflito por última escrita do servidor, mostrar ao professor
    quantos registros estão pendentes.
  - Painel do gestor com frequência por turma e lista de busca ativa.

Etapa 5 — Sustentação
  - Testes: pytest com fixtures de banco efêmero, cobertura mínima de 70%,
    teste específico que prova o isolamento entre dois tenants.
  - CI: ruff, mypy, pytest, build das imagens, publicação no registry.
  - Documentação MkDocs: ADRs das decisões, runbook de restauração de backup,
    manual do professor com capturas de tela.

# PADRÕES DE CÓDIGO
- Nomes de domínio em português (aluno, turma, matricula, frequencia); termos
  técnicos em inglês (router, service, repository). Seja consistente.
- Toda rota precisa de summary, description e dicionário responses preenchidos:
  o /docs é o manual de integração das prefeituras.
- Regra de negócio vive em services/, nunca dentro do router.
- Erro de domínio vira HTTPException com mensagem em português voltada ao usuário
  final; stack trace só no log estruturado.
- Nada de print; use logging com formato JSON.

# ENTREGA
Ao final de cada etapa, gere: o código, os testes correspondentes, a atualização
do README com o comando exato para rodar, e um arquivo docs/adr/NNN-titulo.md
explicando a decisão técnica tomada e as alternativas descartadas.

Comece pela Etapa 1. Antes de escrever código, apresente a árvore de diretórios
proposta e aguarde minha confirmação.
