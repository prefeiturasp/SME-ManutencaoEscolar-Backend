# language: pt

Funcionalidade: API - Lote
  
  Cenário: Criar um novo lote
    Dado que possuo um token de acesso a lote
    E que busco a empresa para o lote
    Quando envio uma requisição POST no endpoint de lote
    Então retorna o status 201 criando um novo lote

  Cenário: Não criar lote sem dados obrigatórios
    Dado que possuo um token de acesso
    Quando envio uma requisição POST no endpoint de lote sem dados obrigatórios
    Então retorna o status 400 sem criar lote
  
  Cenário: Não criar lote sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição POST no endpoint de lote
    Então retorna o status 401 sem criar um novo lote

  Cenário: Atualizar cadastro de lote
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição PUT no endpoint de lote
    Então retorna o status 200 atualizando um lote

  Cenário: Não atualizar lote sem dados obrigatórios
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição PUT no endpoint de lote sem o id
    Então retorna o status 405 sem atualizar lote

  Cenário: Não atualizar lote sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição PUT no endpoint de lote
    Então retorna o status 401 sem atualizar lote

  Cenário: Listar todos lotes
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição GET no endpoint de lote
    Então retorna o status 200 listando todos lotes

  Cenário: Listar somente lotes ativos
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição GET no endpoint de lote status
    Então retorna o status 200 listando somente lotes ativos

  Cenário: Buscar lote por nome
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição GET no endpoint de lote nome
    Então retorna o status 200 buscando por nome do lote  

  Cenário: Não buscar lote sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de lote
    Então retorna o status 401 sem buscar lote

  Cenário: Buscar detalhes do lote
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição GET no endpoint de lote detalhes
    Então retorna o status 200 buscando detalhes do lote
  
  Cenário: Não buscar detalhes de lote inexistente
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição GET no endpoint de lote detalhes inexistente
    Então retorna o status 404 sen detalhes do lote

  Cenário: Não buscar detalhes de lote sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de lote detalhes
    Então retorna o status 401 sem detalhes dos lotes

  Cenário: Excluir cadastro de lote
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição DELETE no endpoint de lote
    Então retorna o status 204 excluindo o lote

  Cenário: Não excluir cadastro de lote sem id
    Dado que possuo um token de acesso a lote
    Quando envio uma requisição DELETE no endpoint de lote sem o id
    Então retorna o status 404 sem excluir o lote

  Cenário: Não excluir lote sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição DELETE no endpoint de lote
    Então retorna o status 401 sem excluir lote