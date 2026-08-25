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
  
  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando clico em criar cadastro de empresa "<status>"
    Então o sistema não salva a empresa sem preenchimento dos campos

    Exemplos:
      | status | caso                                        |
      | ativo  | Não permitir salvar sem campos obrigatórios |

  Esquema do Cenário: Validar campo: <caso>
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