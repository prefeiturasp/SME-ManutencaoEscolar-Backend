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
