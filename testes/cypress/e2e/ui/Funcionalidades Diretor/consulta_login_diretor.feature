# language: pt

Funcionalidade: Acesso de usuário diretor

  Contexto:
    Validação dos cenários e campos obrigatórios
  
  Esquema do Cenário: Validar: <caso>
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"
    Então o sistema valida o "<campo>" no acesso

    Exemplos:
      | campo | caso                        |
      | login | Login realizado com sucesso |

  Esquema do Cenário: Validar: <caso>
    Dado eu acesso o sistema Manutenção Escolar
    Quando tento clicar em entrar na tela de login
    Então o sistema valida "<campo>" como obrigatório no acesso

    Exemplos:
      | campo | caso                       |
      | login | Campo de login obrigatório |
      | senha | Campo de senha obrigatório |

  Esquema do Cenário: Validar: <caso>
    Dado eu acesso o sistema Manutenção Escolar
    Quando tento clicar em entrar na tela de login
    Então o sistema valida a quantidade "<campo>" de caracteres com o valor "<dado>" no acesso

    Exemplos:
      | dado | campo | caso                            |
      | 1234 | login | Mínimo de 7 caracteres no login |
      | 123  | senha | Mínimo de 4 caracteres na senha |

  Esquema do Cenário: Validar: <caso>
    Dado eu acesso o sistema Manutenção Escolar
    Quando tento clicar em entrar na tela de login
    Então o sistema valida "<campo>" inválido "<dado>" no acesso

    Exemplos:
      | dado  | campo   | caso                          |
      | 12345 | login   | Não permitir usuário inválido |
      | 1234  | senha   | Não permitir senha inválida   |