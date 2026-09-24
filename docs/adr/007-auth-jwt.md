# ADR 007: Login JWT e tenant no token

## Decisão

Toda rota de negócio exige Bearer JWT. O token carrega `sub`, `rede_id`, `perfil` e `escola_id`. O frontend deixou de enviar `rede_id`.

Perfis:

- administrador, gestor, diretor, secretaria: cadastro e matrícula
- professor: chamada e leitura
- diretor e professor com `escola_id`: veem só a própria escola

O isolamento entre redes é aplicado na sessão (`SET LOCAL sga.rede_id`) e nas consultas. Políticas RLS foram adicionadas para um role sem `BYPASSRLS`; o usuário `postgres` de desenvolvimento continua superuser e as políticas não o restringem.

A senha usa Argon2. O token dura 8 horas e pode ser renovado em `POST /api/v1/auth/refresh`.

## Alternativas descartadas

- Continuar aceitando `rede_id` no JSON: qualquer cliente escolheria outra prefeitura.
- Cookie de sessão no servidor: pior para o PWA offline e para o proxy.
- Confiar só em RLS com o usuário `postgres`: superuser ignora as políticas.
