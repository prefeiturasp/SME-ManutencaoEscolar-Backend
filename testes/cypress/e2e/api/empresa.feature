# language: pt

Funcionalidade: API - Empresa
  
  Cenário: Criar uma nova empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição POST no endpoint de empresas
    Então retorna o status 201 cadastrando uma empresa

  Cenário: Não criar empresa sem dados obrigatórios
    Dado que possuo um token de acesso
    Quando envio uma requisição POST no endpoint de empresas sem dados obrigatórios
    Então retorna o status 400 sem criar empresa
  
  Cenário: Não criar uma nova empresa sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição POST no endpoint de empresas
    Então retorna o status 401 sem cadastrar empresas

  Cenário: Atualizar uma empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT no endpoint de empresas
    Então retorna o status 200 atualizando uma empresa

  Cenário: Não atualizar uma empresa sem dados obrigatórios
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT no endpoint de empresas sem o id
    Então retorna o status 404 sem atualizar empresa

  Cenário: Não atualizar empresa sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição PUT no endpoint de empresas
    Então retorna o status 401 sem atualizar empresas

  Cenário: Listar todas as empresas
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas
    Então retorna o status 200 listando todas as empresas

  Cenário: Listar somente empresas ativas
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas status
    Então retorna o status 200 listando somente empresas ativas

  Cenário: Buscar por cnpj da empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas cnpj
    Então retorna o status 200 buscando por cnpj da empresa

  Cenário: Buscar por razão social da empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas razão social
    Então retorna o status 200 buscando por razão social da empresa

  Cenário: Buscar por nome da empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas nome
    Então retorna o status 200 buscando por nome da empresa

  Cenário: Não buscar empresas sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de empresas
    Então retorna o status 401 sem buscar empresas

  Cenário: Buscar detalhes da empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas detalhes
    Então retorna o status 200 buscando detalhes da empresa
  
  Cenário: Não buscar detalhes da empresa inexistente
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de empresas detalhes inexistente
    Então retorna o status 404 sen detalhes da empresa

  Cenário: Não buscar detalhes empresas sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no endpoint de empresas detalhes
    Então retorna o status 401 sem detalhes das empresas

  Cenário: Excluir cadastro de uma empresa
    Dado que possuo um token de acesso
    Quando envio uma requisição DELETE no endpoint de empresas
    Então retorna o status 204 excluindo a empresa

  Cenário: Não excluir cadastro de uma empresa sem id
    Dado que possuo um token de acesso
    Quando envio uma requisição DELETE no endpoint de empresas sem o id
    Então retorna o status 404 sem excluir a empresa

  Cenário: Não excluir empresas sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição DELETE no endpoint de empresas
    Então retorna o status 401 sem excluir empresas