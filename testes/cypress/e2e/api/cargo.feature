# language: pt

Funcionalidade: API - Cargo
  
  Cenário: Criar um novo cargo
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição POST no endpoint de cargo
    Então retorna o status 201 criando um novo cargo

  Cenário: Não criar cargo sem dados obrigatórios
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição POST no endpoint de cargo sem dados obrigatórios
    Então retorna o status 400 sem criar cargo
  
  Cenário: Não criar cargo sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição POST no endpoint de cargo
    Então retorna o status 401 sem criar um novo cargo

  Cenário: Atualizar cadastro de cargo
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição PUT no endpoint de cargo
    Então retorna o status 200 atualizando um cargo

  Cenário: Não atualizar cargo sem dados obrigatórios
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição PUT no endpoint de cargo sem o id
    Então retorna o status 405 sem atualizar cargo

  Cenário: Não atualizar cargo sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição PUT no endpoint de cargo
    Então retorna o status 401 sem atualizar cargo

  Cenário: Listar todos cargos
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição GET no endpoint de cargo
    Então retorna o status 200 listando todos cargos

  Cenário: Listar somente cargos ativos
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição GET no endpoint de cargo status
    Então retorna o status 200 listando somente cargos ativos

  Cenário: Buscar cargo por nome
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição GET no endpoint de cargo nome
    Então retorna o status 200 buscando por nome do cargo  

  Cenário: Não buscar cargo sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de cargo
    Então retorna o status 401 sem buscar cargo

  Cenário: Buscar detalhes do cargo
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição GET no endpoint de cargo detalhes
    Então retorna o status 200 buscando detalhes do cargo
  
  Cenário: Não buscar detalhes de cargo inexistente
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição GET no endpoint de cargo detalhes inexistente
    Então retorna o status 404 sen detalhes do cargo

  Cenário: Não buscar detalhes de cargo sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de cargo detalhes
    Então retorna o status 401 sem detalhes dos cargos

  Cenário: Excluir cadastro de cargo
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição DELETE no endpoint de cargo
    Então retorna o status 204 excluindo o cargo

  Cenário: Não excluir cadastro de cargo sem id
    Dado que possuo um token de acesso a cargo
    Quando envio uma requisição DELETE no endpoint de cargo sem o id
    Então retorna o status 404 sem excluir o cargo

  Cenário: Não excluir cargo sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição DELETE no endpoint de cargo
    Então retorna o status 401 sem excluir cargo