# language: pt

Funcionalidade: Cadastro de cargo

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Admin"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando crio cadastro de cargo "<status>"
    Então o sistema salva o cargo

    Exemplos:
      | status | caso                         |
      | ativo  | Cargo cadastrado com sucesso |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando não preencho o cadastro de cargo "<status>"
    Então o sistema não cadastra o cargo sem campos obrigatórios

    Exemplos:
      | status | caso                                 |
      | ativo  | Preenchimento de campos obrigatórios |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando preencho sim em documento de cargo "<status>"
    Então o sistema permite inserir no cargo documentos exigidos

    Exemplos:
      | status | caso            |
      | ativo  | Exige documento |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando cancelo preenchimento o cadastro de cargo "<status>"
    Então o sistema não cadastra o cargo retornando para listagem

    Exemplos:
      | status | caso                               |
      | ativo  | Cancelar preenchimento de cadastro |
     
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando crio cadastro de cargo "<status>"
    Então o sistema informa cargo já cadastrado

    Exemplos:
      | status | caso                        |
      | ativo  | Não permitir nome duplicado |