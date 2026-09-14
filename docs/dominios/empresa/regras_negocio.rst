Esta seção documenta as regras de negócio que orientam o
funcionamento do domínio **Empresa**.

Identificador Único
-------------------

Cada registro do domínio possui um identificador único no formato
**UUID (Universally Unique Identifier)**.

O identificador é gerado automaticamente pelo sistema no momento
da criação do registro e não pode ser alterado manualmente.

O UUID deve ser utilizado para identificar de forma inequívoca
cada registro do domínio.

Auditoria de Criação
--------------------

Os registros possuem informações de auditoria relacionadas à sua
criação.

A data e hora de criação são registradas automaticamente pelo
sistema. Quando disponível, o usuário responsável pela criação
também é registrado.

Auditoria de Atualização
------------------------

Os registros possuem informações de auditoria relacionadas às
alterações realizadas.

A data e hora da última atualização são atualizadas
automaticamente pelo sistema. Quando disponível, o usuário
responsável pela atualização também é registrado.

Exclusão e Restauração
----------------------

Os registros utilizam exclusão lógica para preservar as
informações após uma exclusão.

Ao realizar uma exclusão lógica, o sistema registra a data e hora
da exclusão e, quando disponível, o usuário responsável pela ação.

Registros excluídos logicamente não são retornados pelo
gerenciamento padrão dos objetos.

Registros excluídos podem ser restaurados, retornando ao conjunto
de registros disponíveis para consulta e utilização.
