# language: pt

Funcionalidade: Exclusão de Empresa

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema Manutenção Escolar com perfil "Diretor"    

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando seleciono a empresa "<status>" para excluir
	  E clico em cancelar no modal de excluir empresa
	  Então o sistema cancela exclusão da empresa

    Exemplos:
      | status | caso                         |
      | ativo  | Cancelar exclusão de empresa |

  Esquema do Cenário: Validar: <caso>
    E acesso a tela Empresas
    Quando seleciono na empresa "<status>" para excluir
    Então o sistema exclui a empresa

    Exemplos:
      | status | caso                         |
      | ativo  | Empresa excluída com sucesso |

  


     