# language: pt

Funcionalidade: Exclusão de serviço

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando cancelo a exclusão do cadastro de serviço "<status>"
    Então o sistema não exclui o serviço retornando para os detalhes

    Exemplos:
      | status | caso                          |
      | ativo  | Cancelar exclusão de cadastro |   

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando aciono a exclusão do cadastro de serviço "<status>"
    E fecho o modal de exclusão do serviço
    Então o sistema não exclui o serviço retornando para os detalhes

    Exemplos:
      | status | caso                     |
      | ativo  | Fechar modal de exclusão |   

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando clico para excluir o cadastro de serviço "<status>"
    Então o sistema exclui o serviço

    Exemplos:
      | status | caso                         |
      | ativo  | Serviço excluído com sucesso |