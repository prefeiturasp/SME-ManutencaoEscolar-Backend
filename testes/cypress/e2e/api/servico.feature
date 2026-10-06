# language: pt

Funcionalidade: API - Serviço
  
  Cenário: Criar um novo serviço
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição POST no endpoint de servicos
    Então retorna o status 201 criando um novo serviço

  Cenário: Não criar serviço sem dados obrigatórios
    Dado que possuo um token de acesso
    Quando envio uma requisição POST no endpoint de servicos sem dados obrigatórios
    Então retorna o status 400 sem criar serviço
  
  Cenário: Não criar serviço sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição POST no endpoint de servicos
    Então retorna o status 401 sem criar um novo serviço

  Cenário: Atualizar cadastro de serviço
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição PUT no endpoint de servicos
    Então retorna o status 200 atualizando um serviço

  Cenário: Não atualizar serviço sem dados obrigatórios
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição PUT no endpoint de servicos sem o id
    Então retorna o status 405 sem atualizar serviço

  Cenário: Não atualizar serviço sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição PUT no endpoint de servicos
    Então retorna o status 401 sem atualizar serviço

  Cenário: Listar todos serviços
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição GET no endpoint de servicos
    Então retorna o status 200 listando todos serviços

  Cenário: Listar somente serviços ativos
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição GET no endpoint de servicos status
    Então retorna o status 200 listando somente serviços ativos

  Cenário: Buscar serviço por nome
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição GET no endpoint de servicos nome
    Então retorna o status 200 buscando por nome do serviço  

  Cenário: Não buscar serviço sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de servicos
    Então retorna o status 401 sem buscar serviços

  Cenário: Buscar detalhes do serviço
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição GET no endpoint de servicos detalhes
    Então retorna o status 200 buscando detalhes do serviços
  
  Cenário: Não buscar detalhes de serviço inexistente
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de servicos detalhes inexistente
    Então retorna o status 404 sen detalhes do serviços

  Cenário: Não buscar detalhes de serviço sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de servico detalhes
    Então retorna o status 401 sem detalhes dos serviços

  Cenário: Excluir cadastro de serviço
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição DELETE no endpoint de servico
    Então retorna o status 204 excluindo o serviço

  Cenário: Não excluir cadastro de serviço sem id
    Dado que possuo um token de acesso a servicos
    Quando envio uma requisição DELETE no endpoint de servico sem o id
    Então retorna o status 404 sem excluir o serviço

  Cenário: Não excluir serviço sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição DELETE no endpoint de servico
    Então retorna o status 401 sem excluir serviço