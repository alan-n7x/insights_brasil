# ADR-001: Usar Supabase Session Pooler para conexão PostgreSQL em produção

## Status

Aceita.

## Contexto

O backend Django do Insights Brasil foi implantado no Render e precisava conectar ao PostgreSQL hospedado no Supabase.

Durante o deploy, a aplicação falhou ao executar `python manage.py migrate` porque a conexão direta com o banco não respondia a partir do ambiente do Render. A resolução DNS do host direto do Supabase retornava apenas endereço IPv6, enquanto o ambiente de deploy precisava de conectividade IPv4 funcional para a conexão PostgreSQL.

Além disso, a falha no `migrate` impedia o Gunicorn de iniciar, causando também mensagens de ausência de porta aberta no Render. Esse erro de porta era uma consequência da falha de conexão com o banco, não a causa principal.

## Decisão

Usar o **Supabase Session Pooler** como endpoint de conexão PostgreSQL em produção.

A configuração de produção passa a usar os dados do pooler:

```env
POSTGRES_HOST=<session-pooler-host>
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=<pooler-user>
POSTGRES_PASSWORD=<database-password>
```

No Render, essas variáveis são configuradas diretamente em **Environment Variables**, sem versionar secrets no repositório.

## Consequências positivas

- O backend Django consegue conectar ao PostgreSQL a partir do Render.
- As migrations passam a executar no deploy.
- O Gunicorn passa a iniciar corretamente após `migrate` e `collectstatic`.
- A aplicação fica funcional em produção usando HTTPS no Render e banco remoto no Supabase.
- A solução reduz dependência de suporte IPv6 no ambiente de aplicação.

## Consequências negativas e trade-offs

- A conexão deixa de ser diretamente com o host primário do PostgreSQL e passa por uma camada intermediária.
- É necessário usar o usuário específico do pooler, que pode ser diferente de `postgres`.
- A configuração fica um pouco mais complexa do que uma connection string direta.
- Problemas de autenticação podem ocorrer se a senha do banco ou o usuário do pooler forem configurados incorretamente.

## Alternativas consideradas

### Direct connection do Supabase

Foi inicialmente usada, mas o endpoint direto resolvia apenas para IPv6 no ambiente testado. Isso causou timeout de conexão no deploy.

### Hospedar PostgreSQL no próprio Render

Seria uma alternativa viável, mas o projeto já estava usando Supabase como banco gerenciado. Trocar de banco aumentaria o escopo da entrega.

### Usar infraestrutura com IPv6 garantido

Resolveria a conexão direta, mas adicionaria complexidade operacional desnecessária para o estágio atual do projeto.

## Resultado

A troca para o Session Pooler permitiu concluir o deploy da API Django no Render com PostgreSQL remoto no Supabase.
