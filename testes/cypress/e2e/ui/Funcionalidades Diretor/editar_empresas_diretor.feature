# language: pt

Funcionalidade: Editar empresa

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando seleciono a empresa "<status>" para editar
	  E edito o cadastro da empresa
	  Então o sistema salva a edição da empresa

    Exemplos:
      | status | caso                          |
      | ativo  | Realizar a edição do cadastro |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando seleciono a empresa "<status>" para editar
	  E deixo o campo vazio no cadastro da empresa
	  Então o sistema exibe campo obrigadotório na edição da empresa

    Exemplos:
      | status | caso                         |
      | ativo  | Dados obrigatórios ao editar |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando seleciono a empresa "<status>" para editar
	  E cancelo a edição do cadastro da empresa
	  Então o sistema retorna sem edição da empresa

    Exemplos:
      | status | caso                         |
      | ativo  | Cancelar a edição do cadastro |


  


     