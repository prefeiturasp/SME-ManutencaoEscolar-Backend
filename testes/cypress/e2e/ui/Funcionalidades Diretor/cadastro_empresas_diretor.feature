# language: pt

Funcionalidade: Cadastro de Empresa

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando crio cadastro de empresa "<status>"
    Então o sistema salva a empresa

    Exemplos:
      | status | caso                           |
      | ativo  | Empresa cadastrada com sucesso |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando crio cadastro a empresa "<status>"
    Então o sistema salva a empresa inativa

    Exemplos:
      | status  | caso                            |
      | inativa | Empresa cadastrada como inativa |
  
  Esquema do Cenário: <caso>
    E acesso a tela Empresas
    Quando clico em criar cadastro de empresa "<status>"
    Então o sistema não avançar em empresas sem preenchimento dos campos

    Exemplos:
      | status | caso                                                   |
      | ativo  | Não permitir avançar sem preencher campos obrigatórios |

  Esquema do Cenário: Informações Gerais — Validar campo obrigatório: <caso>
    E acesso a tela Empresas
    Quando valido o campo obrigatório "<campo>" na empresa
    Então o sistema exibe campo obrigatório de empresa

    Exemplos:
      | caso         | campo        |
      | Nome         | nome         |
      | CNPJ         | cnpj         |
      | Razão Social | razao_social |
      | Status       | status       |
      | CEP          | cep          |
      | Logradouro   | logradouro   |
      | Número       | numero       |
      | Cidade       | cidade       |
      | Estado       | estado       |

  Esquema do Cenário: Cadastrar Responsável Técnico: <caso>
    E acesso a tela Empresas
    Quando crio cadastro com responsável técnico "<caso>"
    Então o sistema salva a empresa com responsável técnico

    Exemplos:
      | caso                   |
      | Preposto               |
      | Engenheiro Civil       |
      | Engenheiro Eletricista |

  Esquema do Cenário: Cadastrar mais de um Responsável Técnico 
    E acesso a tela Empresas
    Quando crio cadastro com responsáveis técnicos
    Então o sistema salva a empresa com todos responsáveis

  Esquema do Cenário: <caso>
    E acesso a tela Empresas
    Quando crio cadastro de empresa "<status>"
    Então o sistema não salva a empresa sem preenchimento dos campos

    Exemplos:
      | status | caso                                        |
      | ativo  | Não permitir salvar sem responsável técnico |

  Esquema do Cenário: Responsável Técnico — Validar campo obrigatório: <caso>
    E acesso a tela Empresas
    Quando crio cadastro de empresa "<status>"
    E valido o campo obrigatório "<campo>" de responsáveis na empresa
    Então o sistema exibe campo obrigatório de responsável técnico

    Exemplos:
      | status | caso                | campo |
      | ativo  | Tipo de responsável | tipo  |
      | ativo  | Nome completo       | nome  |
      | ativo  | Telefone            | tel   |
      | ativo  | E-mail              | email |

     