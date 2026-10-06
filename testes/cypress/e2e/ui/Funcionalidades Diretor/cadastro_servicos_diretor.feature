# language: pt

Funcionalidade: Cadastro de serviço

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando crio cadastro de serviço "<status>"
    Então o sistema salva o serviço

    Exemplos:
      | status | caso                           |
      | ativo  | Serviço cadastrado com sucesso |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando não preencho o cadastro de serviço "<status>"
    Então o sistema não cadastra o serviço sem campos obrigatórios

    Exemplos:
      | status | caso                                 |
      | ativo  | Preenchimento de campos obrigatórios |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando cancelo preenchimento o cadastro de serviço "<status>"
    Então o sistema não cadastra o serviço retornando para listagem

    Exemplos:
      | status | caso                               |
      | ativo  | Cancelar preenchimento de cadastro |
     
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando crio cadastro de serviço "<status>"
    Então o sistema informa serviço já cadastrado

    Exemplos:
      | status | caso                        |
      | ativo  | Não permitir nome duplicado |