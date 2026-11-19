# language: pt

Funcionalidade: Edição de cargo

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Admin"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando edito o cadastro de cargo "<status>"
    Então o sistema salva a edição do cargo

    Exemplos:
      | status | caso                        |
      | ativo  | Cargo editado com sucesso |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando apago o preenchimento no cadastro de cargo "<status>"
    Então o sistema informa campos obrigatórios ao salvar a edição do cargo

    Exemplos:
      | status | caso                          |
      | ativo  | Campos obrigatórios ao salvar |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando cancelo a edição do cadastro de cargo "<status>"
    Então o sistema não edita o cargo retornando para listagem

    Exemplos:
      | status | caso                        |
      | ativo  | Cancelar edição de cadastro |
	  
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando insiro os mesmos dados do cargo "<status>"
    Então o sistema informa cargo existente ao tentar salvar

    Exemplos:
      | status | caso                          |
      | ativo  | Não salvar com nome existente |