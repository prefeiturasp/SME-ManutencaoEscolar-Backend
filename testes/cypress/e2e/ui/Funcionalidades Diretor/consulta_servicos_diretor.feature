# language: pt

Funcionalidade: Consulta de serviço

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Filtrar por: <caso>
    E acesso a tela Serviços
    Quando filtro o nome do serviço "<status>"
    Então o sistema retorna o serviço

    Exemplos:
      | status | caso            |
      | ativo  | Nome do serviço |

  Esquema do Cenário: Filtrar por: <caso>
    E acesso a tela Serviços
    Quando filtro o status do serviço "<status>"
    Então o sistema retorna o serviço ativo

    Exemplos:
      | status | caso   |
      | ativo  | Status |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando cancelo o filtro de serviço "<status>"
    Então o sistema retorna todos serviços na listagem

    Exemplos:
      | status | caso           |
      | ativo  | Limpar filtros |

  Esquema do Cenário: Exibir: <caso>
    E acesso a tela Serviços
    Quando clico no cadastro de serviço "<status>"
    Então o sistema exibe os detalhes do serviço

    Exemplos:
      | status | caso                         |
      | ativo  | Detalhes do serviço |
	  
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Serviços
    Quando filtro dados do serviço inexistente
    Então o sistema informa que serviço não foi encontrado

    Exemplos:
      | caso                           |
      | Dados não encontrados na busca |