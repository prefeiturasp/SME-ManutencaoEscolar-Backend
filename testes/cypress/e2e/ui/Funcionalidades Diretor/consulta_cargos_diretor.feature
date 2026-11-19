# language: pt

Funcionalidade: Consulta de cargo

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Admin"    

  Esquema do Cenário: Filtrar por: <caso>
    E acesso a tela Cargos
    Quando filtro o nome do cargo "<status>"
    Então o sistema retorna o cargo

    Exemplos:
      | status | caso            |
      | ativo  | Nome do cargo |

  Esquema do Cenário: Filtrar por: <caso>
    E acesso a tela Cargos
    Quando filtro documento do cargo "<tipo>"
    Então o sistema retorna o cargo não exigido

    Exemplos:
      | tipo | caso            |
      | Não  | Exige documento |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando cancelo o filtro de cargo "<status>"
    Então o sistema retorna todos cargos na listagem

    Exemplos:
      | status | caso           |
      | ativo  | Limpar filtros |

  Esquema do Cenário: Exibir: <caso>
    E acesso a tela Cargos
    Quando clico no cadastro de cargo "<status>"
    Então o sistema exibe os detalhes do cargo

    Exemplos:
      | status | caso              |
      | ativo  | Detalhes do cargo |
	  
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Cargos
    Quando filtro dados do cargo inexistente
    Então o sistema informa que cargo não foi encontrado

    Exemplos:
      | caso                           |
      | Dados não encontrados na busca |