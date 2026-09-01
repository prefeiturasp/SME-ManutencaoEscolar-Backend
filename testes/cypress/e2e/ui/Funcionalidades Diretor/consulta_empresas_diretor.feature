# language: pt

Funcionalidade: Consulta de Empresa

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando clico no cadastro de empresa "<status>"
    Então o sistema exibe os detalhes da empresa

    Exemplos:
      | status | caso                       |
      | ativo  | Exibir detalhes da empresa |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando clico no rastrear empresa "<status>"
    Então o sistema direciona ao rastreio da empresa

    Exemplos:
      | status  | caso             |
      | inativa | Rastrear empresa |
  
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando clico limpar filtros de empresa
    Então o sistema retorna a listagem de empresas

    Exemplos:
    | caso           |
    | Limpar filtros |

  Esquema do Cenário: Buscar por: <caso>
    E acesso a tela Empresas
    Quando filtro por "<campo>" na empresa
    Então o sistema busca por "<campo>" o cadastro de emrpesa

    Exemplos:
      | caso         | campo        |
      | Nome         | nome         |
      | CNPJ         | cnpj         |
      | Razão Social | razao_social |
      | Status       | status       |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando filtro por "<campo>" inexistente na empresa
    Então o sistema não busca por "<campo>" no cadastro de emrpesa

    Exemplos:
      | caso                  | campo |
      | Dados não encontrados | cnpj  |

