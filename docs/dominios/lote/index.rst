=====
Lotes
=====

Visão geral
===========

O módulo de lotes gerencia o cadastro de lotes associados a empresas e
Diretorias Regionais de Educação (DREs).

Cada lote possui um código de cadastro, nome, situação, empresa responsável,
período de vigência e um conjunto de DREs vinculadas. O módulo disponibiliza
operações de consulta, criação, alteração parcial e exclusão lógica, além de
um processo automático para inativar lotes com período encerrado.

Responsabilidades
-----------------

* cadastrar lotes e associá-los a uma empresa;
* vincular uma ou mais DREs aos lotes;
* impedir que uma DRE vinculada a um lote ativo e não excluído seja associada
  a outro lote;
* consultar lotes com filtros e paginação;
* atualizar parcialmente os dados e vínculos de um lote;
* realizar a exclusão lógica de lotes;
* registrar os usuários responsáveis pela criação, atualização e exclusão;
* inativar lotes cujo período final tenha terminado.

Arquitetura funcional
---------------------

::

    Lotes
    |
    +-- Consulta
    |   +-- Listagem paginada
    |   +-- Consulta individual por UUID
    |   +-- Filtros por identificação, situação e relacionamentos
    |   +-- Filtros por período
    |
    +-- Cadastro
    |   +-- Validação dos dados
    |   +-- Associação com empresa
    |   +-- Validação das DREs
    |   +-- Criação dos vínculos
    |
    +-- Atualização
    |   +-- Alteração parcial dos dados
    |   +-- Validação das DREs
    |   +-- Sincronização dos vínculos
    |
    +-- Exclusão
    |   +-- Registro do usuário responsável
    |   +-- Exclusão lógica
    |
    +-- Validade
        +-- Task Celery
        +-- Comando de verificação
        +-- Inativação dos lotes vencidos


Principais fluxos
-----------------

Cadastro de lote
~~~~~~~~~~~~~~~~

::

    Cliente
       |
       v
    POST /lotes
       |
       +-- Validação dos campos e do período
       +-- Validação de DREs repetidas
       |
       v
    Serviço de lotes
       |
       +-- Remove espaços externos do nome e do código
       +-- Verifica vínculos com outros lotes ativos
       |
       v
    Persistência transacional
       |
       +-- Cria o lote
       +-- Cria os vínculos com as DREs
       |
       v
    Resposta do cadastro

O cadastro recebe a empresa por UUID e as DREs por seus identificadores
numéricos. O nome e o código têm seus espaços externos removidos antes da
persistência.

A criação do lote e de seus vínculos ocorre em uma única transação. Se uma
das DREs estiver associada a outro lote ativo e não excluído, a operação é
rejeitada e a resposta identifica as DREs indisponíveis e os respectivos
códigos dos lotes.

Atualização de lote
~~~~~~~~~~~~~~~~~~~

::

    Cliente
       |
       v
    PATCH /lotes/{uuid}
       |
       +-- Validação dos dados recebidos
       +-- Validação dos novos vínculos
       |
       v
    Atualização do lote
       |
       +-- Alteração dos campos
       +-- Remoção dos vínculos não mantidos
       +-- Criação dos novos vínculos
       +-- Registro do usuário responsável
       |
       v
    Resposta da atualização

Quando uma lista não vazia de DREs é enviada, os vínculos atuais que não
estiverem nessa lista são removidos e os novos vínculos são criados. A
validação de exclusividade desconsidera o próprio lote que está sendo
alterado.

O comportamento para uma lista vazia de DREs apresenta uma limitação descrita
em ``Observações``.

Exclusão de lote
~~~~~~~~~~~~~~~~

::

    Cliente
       |
       v
    DELETE /lotes/{uuid}
       |
       +-- Identificação do usuário
       +-- Registro do responsável
       |
       v
    Exclusão lógica
       |
       v
    Resposta sem conteúdo

A exclusão mantém o lote persistido e registra o usuário responsável. O
comportamento completo de visibilidade e restauração depende da implementação
compartilhada de exclusão lógica, que não fez parte dos arquivos analisados.

Inativação por vencimento
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    Task Celery
       |
       v
    Comando inativar_lotes_expirados
       |
       +-- Localiza lotes ativos
       +-- Ignora lotes excluídos
       +-- Compara o período final com a data atual
       |
       v
    Altera a situação para inativa

O processo considera vencido o lote cujo período final seja anterior à data
local da execução. Lotes que vencem na própria data da execução ainda não são
inativados.

Entidades
---------

Lote
~~~~

Representa o agrupamento associado a uma empresa e às DREs atendidas.

Os campos funcionalmente relevantes são:

* ``uuid``: identificador utilizado nas operações individuais da API;
* ``codigo_cadastro``: código de identificação do lote;
* ``nome``: denominação do lote;
* ``status``: indica se o lote está ativo ou inativo;
* ``empresa``: empresa associada ao lote;
* ``periodo_inicial``: início opcional do período de vigência;
* ``periodo_final``: término opcional do período de vigência.

O código e o nome aceitam até 255 caracteres. Os lotes são criados como
ativos quando o status não é informado.

LoteDiretoriaRegional
~~~~~~~~~~~~~~~~~~~~~

Representa a associação entre um lote e uma DRE. A existência dessa entidade
permite que um lote possua diversas DREs.

A exclusão física de um lote remove seus vínculos em cascata. Uma DRE
referenciada por um vínculo não pode ser fisicamente removida enquanto a
referência existir.

A exclusividade funcional da DRE é validada pela aplicação considerando
somente vínculos com lotes ativos e não excluídos.

Empresa
~~~~~~~

Representa a empresa responsável pelo lote. A empresa é informada pelo UUID
no cadastro e na atualização, mas é apresentada de forma detalhada nas
consultas.

Uma empresa associada a um lote não pode ser fisicamente excluída enquanto
a referência existir.

Integrações
-----------

Core
~~~~

O módulo utiliza o domínio Core para UUID, auditoria, exclusão lógica.

Usuários
~~~~~~~~

O usuário autenticado é associado às operações de criação, atualização e exclusão. O envio de anexos também valida a existência do usuário responsável.

Empresa
~~~~~~~

O módulo utiliza o domínio de empresas para validar e apresentar a empresa
associada ao lote.

No cadastro e na alteração, a empresa deve corresponder a um UUID existente.
Nas respostas de consulta, seus dados são apresentados pelo serializer do
domínio de empresas.

Diretoria Regional
~~~~~~~~~~~~~~~~~~

O módulo utiliza o domínio de escolas para validar e apresentar as DREs
associadas ao lote.

As DREs são informadas por identificadores numéricos. Identificadores
inexistentes são rejeitados durante a validação da requisição.

Celery e comandos Django
~~~~~~~~~~~~~~~~~~~~~~~~

A task ``executar_validade_lote`` executa o comando
``inativar_lotes_expirados``. O comando verifica a validade dos lotes e
inativa os vencidos.

Será executado uma vez ao dia conforme a regra de agendamento definida no Celery Beat. O comando registra em log o início e a conclusão da verificação,
a quantidade de lotes vencidos encontrados.

Permissões e acesso
-------------------

As operações de criação, atualização e exclusão exigem que
``request.user`` seja uma instância válida de usuário da aplicação. Caso
contrário, a operação é rejeitada como não autenticada.

Processamento assíncrono
------------------------

A task Celery ``executar_validade_lote`` delega a execução ao comando
``inativar_lotes_expirados``.

O comando registra em log:

* o início da verificação;
* a quantidade de lotes vencidos encontrados;
* os lotes processados;
* a conclusão da verificação.

Não existe política explícita de retry na task analisada.

Auditoria
---------

Na criação, o usuário autenticado é registrado como responsável pela criação
e pela última atualização do lote.

Na atualização, o usuário autenticado é registrado como responsável pela
alteração.

Na exclusão lógica, o usuário autenticado é registrado como responsável pela
exclusão.

As consultas apresentam os identificadores e nomes dos usuários responsáveis,
além das datas de criação e atualização fornecidas pelo modelo base.

Estados e transições
--------------------

O lote possui dois estados representados pelo campo ``status``:

* ativo;
* inativo.

Quando o status não é informado no cadastro, o lote inicia ativo. O cadastro
e a atualização permitem informar explicitamente qualquer um dos dois
estados.

A inativação automática executa a seguinte transição:

::

    ATIVO
      |
      | período final anterior à data atual
      v
    INATIVO

Não foram identificadas restrições que impeçam a reativação manual de um lote
por meio de alteração parcial.

Regras de Negócio
=================

Esta seção apresenta as regras de negócio que orientam o
funcionamento do domínio **Lote**.

As regras descrevem comportamentos, restrições, validações
e condições que precisam ser respeitados pelas funcionalidades
do domínio.

.. toctree::
   :maxdepth: 1

   regras_negocio

Documentação do código
======================

Esta seção apresenta a documentação técnica dos componentes que
implementam o domínio **Lote**.

A documentação é gerada automaticamente a partir dos módulos
Python do app e tem como objetivo facilitar a compreensão da
implementação e de suas responsabilidades técnicas.

.. toctree::
   :maxdepth: 1

   codigo/index
