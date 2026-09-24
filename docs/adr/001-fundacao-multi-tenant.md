# ADR 001: Fundação do backend multi-tenant por rede_id

- Status: Aceito
- Data: 2026-09-21

## Contexto

O SGA-EDU atende múltiplas prefeituras em uma mesma instância, com isolamento obrigatório por rede. A operação em municípios com conectividade instável exige segurança e simplicidade de manutenção, além de manutenção por equipe pequena e rotativa.

## Decisão

A aplicação usa um esquema PostgreSQL chamado sga, com a coluna rede_id em todos os dados sensíveis e o valor do tenant vindo do JWT. A camada de aplicação não filtra tenant manualmente; o contexto é aplicado por uma dependência de tenancy e por políticas de Row Level Security (RLS) no banco.

A lógica de segurança centraliza:

- Argon2 para hash de senha.
- JWT contendo rede_id, perfil e escola_id.
- contexto de tenant em variável de contexto da aplicação.
- comandos SQL para set_config('sga.rede_id', ...) antes da consulta.

## Alternativas descartadas

1. Filtrar rede_id no código de cada query.
   - Descartado porque espalha lógica de política entre camadas, aumenta risco de esquecimento e dificulta auditoria.

2. Usar um banco separado por prefeitura.
   - Descartado porque aumenta custo operacional e dificulta manutenção de backups, upgrades e observabilidade.

3. Injetar rede_id em cada query manualmente no repository.
   - Descartado pela mesma razão da alternativa 1: requisito de segurança crítico em código replicado e fácil de omitir.

## Consequências

- O banco garante o isolamento do tenant de forma centralizada.
- A aplicação se torna mais simples, porque os repositories não precisam repetir filtros.
- Os testes podem validar o isolamento com duas redes distintas e verificar a política de segurança.
