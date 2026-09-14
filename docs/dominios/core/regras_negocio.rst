Esta seção documenta as regras de negócio que orientam o
funcionamento do domínio **Core**.

Identificação e auditoria
-------------------------

Todo registro baseado na estrutura de modelo do Core deve possuir um UUID
único gerado automaticamente pelo sistema.

O UUID de um registro não pode ser alterado manualmente após sua criação.

A criação de um registro deve registrar a data e hora da operação. Quando houver usuário autenticado
responsável pela operação, o usuário também deve ser registrado.

A alteração de um registro deve atualizar a data e hora da última alteração. Quando houver usuário autenticado
responsável pela operação, o usuário também deve ser registrado.

A exclusão de um registro deve registrar a data e hora da exclusão. Quando houver usuário autenticado responsável pela operação,
o usuário responsável também deve ser registrado.

Exclusão lógica
---------------

A exclusão de registros do Core deve ser realizada logicamente, sempre que
o modelo utilizar a estrutura de soft delete.

A exclusão lógica não deve remover fisicamente o registro do banco de dados.

Registros excluídos logicamente não devem ser retornados pelas consultas
realizadas através do gerenciador padrão.

Registros excluídos logicamente devem permanecer disponíveis para consultas
administrativas ou operações que utilizem o gerenciador de registros
excluídos.

Um registro excluído logicamente pode ser restaurado.

A restauração deve remover as informações que caracterizam o registro como
excluído.

Autenticação
------------

O usuário deve informar um identificador e uma senha para realizar a
autenticação.

O identificador utilizado no login deve corresponder a um Registro
Funcional (RF) de 7 dígitos ou a um CPF de 11 dígitos.

As credenciais de autenticação devem ser validadas pelo EOL/CoreSSO.

O Core não deve considerar o usuário autenticado somente com base na
validação local.

Uma autenticação realizada com sucesso deve permitir que o Core obtenha os
dados necessários do usuário através das integrações configuradas.

Após uma autenticação bem-sucedida, o Core deve sincronizar no sistema local
as informações necessárias para representar o usuário autenticado.

Uma autenticação bem-sucedida deve gerar um access token e um refresh token.

O access token deve possuir período de validade definido pela configuração
de segurança da aplicação.

O refresh token deve possuir período de validade definido pela configuração
de segurança da aplicação.

Renovação de sessão
-------------------

A renovação da sessão deve utilizar um refresh token válido.

Refresh tokens inválidos ou expirados não podem ser utilizados para gerar
uma nova sessão.

Refresh tokens revogados não podem ser utilizados para gerar uma nova
sessão.

O refresh token utilizado na renovação deve estar associado a um usuário
válido.


A renovação da sessão deve respeitar as regras de autorização vigentes para
o usuário.

Logout
------

O logout deve receber um refresh token válido para realizar a revogação da
sessão.

O refresh token utilizado no logout deve pertencer ao usuário autenticado
que está realizando a operação.

Um refresh token submetido por usuário diferente do seu proprietário não
deve ser revogado em nome desse usuário.

Após o logout, o refresh token deve ser considerado revogado e não poderá
ser utilizado novamente para renovação da sessão.

Recuperação de senha
--------------------

A solicitação de recuperação de senha deve identificar um usuário através
de RF ou CPF válido.

O usuário identificado na solicitação de recuperação deve existir no
sistema.

O usuário deve possuir um endereço de e-mail disponível para que a
recuperação de senha possa ser realizada.

A API não deve expor o endereço de e-mail completo do usuário durante o
fluxo de recuperação de senha.

Quando o endereço for apresentado ao usuário, ele deve ser mascarado.

A recuperação de senha deve utilizar um token específico para redefinição
de senha.

O token de recuperação de senha deve possuir validade limitada.

A validade atualmente definida para o fluxo é de 6 horas.

Um token de recuperação inválido ou expirado não pode ser utilizado para
alterar a senha do usuário.

A nova senha e sua confirmação devem possuir o mesmo valor.

A alteração efetiva da senha deve ser realizada através da integração com
o CoreSSO.

A confirmação de uma alteração de senha somente deve ser considerada
bem-sucedida após o CoreSSO confirmar a operação.

Arquivos e anexos
-----------------

Um anexo deve estar associado a um usuário válido quando essa associação
for exigida pelo fluxo de upload.

Arquivos vazios não podem ser armazenados.

Arquivos sem nome não podem ser armazenados.

O tamanho máximo permitido para um arquivo é de 2 MiB.

Somente extensões previamente configuradas podem ser armazenadas.


As extensões atualmente permitidas são:

* ``.jpg``
* ``.jpeg``
* ``.png``
* ``.pdf``


O nome original do arquivo deve ser preservado nos metadados do anexo.

O nome físico utilizado para armazenar o arquivo não deve depender
diretamente do nome fornecido pelo usuário.

O sistema deve gerar um identificador único para o arquivo armazenado.

O caminho de armazenamento não deve ser determinado arbitrariamente pelo
nome fornecido pelo usuário.

O tipo MIME do arquivo deve ser identificado e registrado nos metadados do
anexo.

Quando não for possível determinar o tipo MIME do arquivo, deve ser
utilizado ``application/octet-stream``.

Os arquivos devem ser armazenados em storage privado.

O conteúdo do arquivo e seus metadados devem ser tratados como informações
distintas.

O banco de dados deve armazenar os metadados necessários para identificar o
arquivo, enquanto o conteúdo deve permanecer no storage configurado.

E-mails
-------

O envio de e-mails deve ser realizado de forma assíncrona quando o fluxo
não exigir o envio dentro do ciclo da requisição HTTP.

Falhas transitórias no processamento de e-mails devem permitir novas
tentativas de processamento.

O envio de e-mail de recuperação de senha não deve impedir a execução de
outras operações independentes da aplicação.

Integração com sistemas externos
--------------------------------

As operações de autenticação dependentes do EOL/CoreSSO devem tratar
explicitamente falhas de comunicação com o serviço externo.

Timeouts na comunicação com serviços externos não devem ser tratados como
autenticação bem-sucedida.

Falhas de integração devem ser convertidas em respostas compatíveis com o
contrato da API, sem expor detalhes internos desnecessários.

As operações que dependem de informações externas somente devem ser
consideradas concluídas após confirmação do serviço externo.

Health Check
------------

O endpoint de health check deve permanecer acessível sem autenticação.

Quando a aplicação estiver operacional, o health check deve indicar o
estado ``ok``.

Consistência documental
-----------------------

Os limites de arquivos documentados devem corresponder aos limites
efetivamente aplicados pela aplicação.

Alterações nas regras de negócio devem ser refletidas neste documento,
independentemente da implementação técnica utilizada.

A documentação OpenAPI e demais documentações técnicas devem permanecer
consistentes com as regras de negócio vigentes.

Observações
-----------

O limite atualmente implementado para arquivos é de 2 MiB.

Caso exista documentação técnica indicando limite diferente, como 10 MB,
a documentação deve ser corrigida ou a regra de implementação deve ser
alterada para eliminar a inconsistência.

A categoria de arquivo ``compactado`` pode existir como tipo conceitual,
mas somente deve ser considerada uma categoria válida para upload quando
houver extensões explicitamente habilitadas e respectivas regras de
validação.


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
