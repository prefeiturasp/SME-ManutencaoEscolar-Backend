Esta seção documenta as regras de negócio que orientam o funcionamento do domínio **Empresa**.

Identificação e auditoria
-------------------------

Empresas, responsáveis técnicos e anexos possuem um UUID único, gerado
automaticamente pelo sistema.

A criação e a atualização registram, quando disponível, o usuário autenticado
responsável pela operação e suas respectivas datas. A exclusão lógica registra
a data e o usuário responsável.

Cadastro da empresa
-------------------

O cadastro de uma empresa deve informar:

* nome e razão social;
* CNPJ;
* status;
* CEP, logradouro, número, cidade e estado;
* ao menos um responsável técnico.

O complemento do endereço é opcional. O link de rastreio também é opcional e,
quando informado, deve ser uma URL válida.

O CNPJ deve possuir formato válido e não pode estar associado a outra empresa
que não tenha sido excluída logicamente. Na atualização, a própria empresa é
desconsiderada nessa verificação. O CNPJ de uma empresa excluída logicamente
pode ser reutilizado.

O CEP deve conter exatamente oito dígitos numéricos. O estado deve ser uma das
unidades federativas aceitas pela aplicação.

Empresas são criadas como ativas por padrão. A listagem apresenta primeiro as
empresas ativas e, dentro de cada situação, os registros mais recentes.

Responsáveis técnicos
---------------------

Cada responsável técnico pertence a uma empresa e deve possuir nome, tipo,
e-mail e telefone. Os tipos permitidos são:

* ``preposto``;
* ``engenheiro_civil``;
* ``engenheiro_eletricista``.

O telefone deve conter dez ou onze dígitos numéricos. Os campos de número do
CREA e número da ART são opcionais para o tipo preposto.

Uma empresa deve possuir ao menos um responsável técnico. Não é permitido
informar mais de um responsável do mesmo tipo no cadastro da empresa.

Engenheiros civis e engenheiros eletricistas devem possuir ao menos um anexo.
Essa obrigatoriedade não se aplica ao preposto.

Sincronização dos responsáveis técnicos
---------------------------------------

Na atualização de uma empresa, os responsáveis técnicos são sincronizados a
partir da lista enviada:

* um item com UUID atualiza o responsável correspondente;
* um item sem UUID cria um novo responsável;
* um responsável existente que não consta na lista é excluído logicamente.

Todo UUID informado deve pertencer a um responsável técnico da própria
empresa. Caso contrário, a atualização é rejeitada.

A criação da empresa e de seus responsáveis, assim como a atualização do
conjunto, ocorre em uma transação. Se alguma etapa falhar, as alterações no
banco de dados são revertidas.

Anexos dos responsáveis técnicos
--------------------------------

Os anexos pertencem a um responsável técnico e utilizam as validações comuns
de arquivo fornecidas pelo domínio Core, incluindo extensão, tamanho e tipo
MIME.

Na sincronização dos anexos:

* um anexo informado por UUID é preservado;
* um arquivo novo, sem UUID, é validado e armazenado;
* um anexo existente que não consta na lista é excluído.

Os metadados do anexo são mantidos no banco de dados, enquanto o conteúdo é
armazenado no storage privado configurado. A resposta expõe o UUID, o nome
original, a URL do arquivo e os dados de auditoria do anexo.

A remoção física do arquivo do storage ocorre somente após a confirmação da
transação no banco de dados.

Exclusão lógica
---------------

A exclusão de uma empresa não remove fisicamente seu registro. A empresa e
seus responsáveis técnicos são marcados como excluídos e deixam de aparecer
nas consultas realizadas pelos gerenciadores padrão.

Antes da exclusão lógica de cada responsável, seus anexos são removidos. Toda
a operação de exclusão da empresa é transacional para evitar um estado
parcial em caso de falha.

Consulta e filtros
------------------

As operações da API exigem autenticação. A consulta de uma empresa utiliza o
UUID como identificador público; um UUID inexistente retorna resposta de
recurso não encontrado.

A listagem permite os seguintes filtros:

* ``nome``: correspondência parcial, sem diferenciar maiúsculas e minúsculas;
* ``razao_social``: correspondência parcial, sem diferenciar maiúsculas e
  minúsculas;
* ``cnpj``: correspondência parcial;
* ``status``: correspondência exata por valor booleano.
