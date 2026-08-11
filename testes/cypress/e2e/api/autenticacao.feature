# language: pt

Funcionalidade: API - Autenticação

  Cenário: Realiza a autenticação com sucesso
    Dado que acesso o endpoint de autenticação
    Quando envio os dados de acesso
    Então retorna status 200 com o token válido

  Cenário: Login deve ser obrigatório
    Dado que acesso o endpoint de autenticação
    Quando envio os dados sem o login
    Então retorna status 400 que acesso foi inválido

  Cenário: Senha deve ser obrigatória
    Dado que acesso o endpoint de autenticação
    Quando envio os dados sem a senha
    Então retorna status 400 que é necessário ser informada
  
  Cenário: Não autenticar com usuário inválido
    Dado que acesso o endpoint de autenticação
    Quando envio os dados com usuário inválido
    Então retorna status 401 retorna sem acessar com usuário

  Cenário: Não autenticar com senha inválida
    Dado que acesso o endpoint de autenticação
    Quando envio os dados com senha inválida
    Então retorna status 401 retorna sem acessar com senha