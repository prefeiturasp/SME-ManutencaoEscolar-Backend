# language: pt

Funcionalidade: Edição de serviço

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando edito o cadastro de serviço "<status>"
    Então o sistema salva a edição do serviço

    Exemplos:
      | status | caso                        |
      | ativo  | Serviço editado com sucesso |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando cancelo edição do cadastro de serviço "<status>"
    Então o sistema não edita o serviço retornando para listagem

    Exemplos:
      | status | caso                        |
      | ativo  | Cancelar edição de cadastro |
	  
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando insiro os mesmos dados do serviço "<status>"
    Então o sistema informa serviço ao tentar salvar o serviço

    Exemplos:
      | status | caso                          |
      | ativo  | Não salvar com nome existente |