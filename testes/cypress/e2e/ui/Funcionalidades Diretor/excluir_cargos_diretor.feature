# language: pt

Funcionalidade: Exclusão de cargo

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Admin"

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando cancelo a exclusão do cadastro de cargo "<status>"
    Então o sistema não exclui o cargo retornando para os detalhes

    Exemplos:
      | status | caso                          |
      | ativo  | Cancelar exclusão de cadastro |   

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando aciono a exclusão do cadastro de cargo "<status>"
    E fecho o modal de exclusão do cargo
    Então o sistema não exclui o cargo retornando para os detalhes

    Exemplos:
      | status | caso                     |
      | ativo  | Fechar modal de exclusão | 

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando clico para excluir o cadastro de cargo  de profissionais "<status>"
    Então o sistema não exclui cargo vinculado

    Exemplos:
      | status | caso                                  |
      | ativo  | Não excluir vinculado a profissionais |  

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando clico para excluir o cadastro de cargo "<status>"
    Então o sistema exclui o cargo

    Exemplos:
      | status | caso                       |
      | ativo  | Cargo excluído com sucesso |