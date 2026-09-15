========
Empresas
========

Visão geral
===========

O módulo de empresas gerencia o cadastro das empresas prestadoras de serviço,
seus responsáveis técnicos e os anexos associados a esses responsáveis.

Cada empresa possui dados cadastrais, endereço, situação e, opcionalmente, um
link de rastreio. O módulo disponibiliza operações de consulta, criação,
atualização integral e exclusão lógica, além da sincronização dos responsáveis
técnicos e de seus arquivos.

Responsabilidades
-----------------

* cadastrar empresas com seus responsáveis técnicos;
* validar CNPJ, CEP, endereço e link de rastreio;
* impedir a repetição de CNPJ entre empresas não excluídas;
* consultar empresas com filtros e paginação;
* atualizar integralmente os dados de uma empresa;
* sincronizar responsáveis técnicos e seus anexos;
* realizar a exclusão lógica de empresas e responsáveis técnicos;
* registrar os usuários responsáveis pela criação, atualização e exclusão.

Arquitetura funcional
---------------------

::

    Empresas
    |
    +-- Consulta
    |   +-- Listagem paginada
    |   +-- Consulta individual por UUID
    |   +-- Filtros por nome, razão social, CNPJ e status
    |
    +-- Cadastro
    |   +-- Validação dos dados cadastrais e do endereço
    |   +-- Validação dos responsáveis técnicos
    |   +-- Criação transacional da empresa e dos responsáveis
    |   +-- Armazenamento dos anexos dos responsáveis técnicos
    |
    +-- Atualização
    |   +-- Alteração integral dos dados
    |   +-- Sincronização dos responsáveis por UUID
    |   +-- Sincronização dos anexos por UUID
    |
    +-- Exclusão
        +-- Remoção dos anexos
        +-- Exclusão lógica dos responsáveis
        +-- Exclusão lógica da empresa
        +-- Registro do usuário responsável pela ação

Principais fluxos
-----------------

Cadastro de empresa
~~~~~~~~~~~~~~~~~~~

::

    Cliente
       |
       v
    POST /empresas
       |
       +-- Validação dos dados da empresa
       +-- Validação da lista de responsáveis
       +-- Validação dos anexos
       |
       v
    Serviço de empresas
       |
       +-- Registra o usuário responsável
       +-- Separa os dados da empresa, responsáveis e anexos para persistência
       |
       v
    Persistência transacional
       |
       +-- Cria a empresa
       +-- Cria os responsáveis técnicos
       +-- Cria e armazena os novos anexos
       |
       v
    Resposta do cadastro

O cadastro exige ao menos um responsável técnico e não aceita tipos repetidos
na mesma requisição. A empresa e seus responsáveis são criados em uma única
transação, com o usuário autenticado registrado na auditoria.

Engenheiros civis e engenheiros eletricistas devem receber ao menos um anexo.
O preposto pode ser cadastrado sem arquivos.

Atualização de empresa
~~~~~~~~~~~~~~~~~~~~~~

::

    Cliente
       |
       v
    PUT /empresas/{uuid}
       |
       +-- Validação integral dos dados
       +-- Validação dos UUIDs dos responsáveis
       |
       v
    Atualização transacional
       |
       +-- Atualiza a empresa
       +-- Atualiza responsáveis com UUID
       +-- Cria responsáveis sem UUID
       +-- Remove responsáveis omitidos
       +-- Preserva anexos com UUID
       +-- Cria anexos sem UUID
       +-- Remove anexos omitidos
       +-- Registro do usuário responsável
       |
       v
    Resposta da atualização

Os responsáveis técnicos são sincronizados a partir da lista enviada. Um item
com UUID atualiza o registro correspondente, enquanto um item sem UUID cria um
novo responsável. Responsáveis existentes que não estejam na lista são
excluídos logicamente.

O UUID informado deve pertencer a um responsável da própria empresa. A lista
de anexos também é sincronizada: itens com UUID são preservados, novos arquivos
são criados e anexos omitidos são removidos.

Exclusão de empresa
~~~~~~~~~~~~~~~~~~~

::

    Cliente
       |
       v
    DELETE /empresas/{uuid}
       |
       +-- Remoção dos anexos dos responsáveis
       +-- Remoção dos anexos armazenados no storage
       +-- Exclusão lógica dos responsáveis
       |
       v
    Exclusão lógica da empresa
       |
       v
    Resposta sem conteúdo

A exclusão preserva os registros da empresa e de seus responsáveis no banco de
dados, marcando-os como excluídos. Os respectivos anexos são removidos, e os
arquivos são apagados do storage após a confirmação da transação.

Entidades
---------

Empresa
~~~~~~~

Representa a empresa prestadora de serviço. Seus campos funcionalmente
relevantes são:

* ``uuid``: identificador utilizado nas operações individuais da API;
* ``nome`` e ``razao_social``: identificação da empresa;
* ``cnpj``: cadastro nacional sem pontuação, com 14 dígitos;
* ``status``: indica se a empresa está ativa ou inativa;
* ``link_rastreio``: URL opcional para rastreamento;
* ``cep``, ``logradouro``, ``numero``, ``complemento``, ``cidade`` e
  ``estado``: informações do endereço da empresa.

Empresas são criadas como ativas quando o status não é informado. A ordenação
padrão apresenta primeiro as empresas ativas e, dentro de cada situação, os
registros de maior identificador (id) numérico.

Responsável técnico
~~~~~~~~~~~~~~~~~~~

Representa uma pessoa tecnicamente responsável por uma empresa. Os tipos
permitidos são ``preposto``, ``engenheiro_civil`` e
``engenheiro_eletricista``.

Além do tipo e do nome, o responsável possui e-mail, telefone e campos
opcionais para os números do CREA e da ART. A exclusão física de uma empresa
remove seus responsáveis em cascata, embora o fluxo da API utilize exclusão
lógica.

Anexo do responsável técnico
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Representa um arquivo vinculado a um responsável técnico. O registro mantém o
nome original, o tipo, o tipo MIME, o tamanho e a referência ao objeto salvo no
storage privado.

São aceitos arquivos ``.jpg``, ``.jpeg``, ``.png`` e ``.pdf`` com até 2 MB.
O nome físico do arquivo é gerado com UUID, preservando sua extensão.

Integrações
-----------

Core
~~~~

O módulo utiliza o domínio Core para UUID, auditoria, exclusão lógica,
validação de CNPJ, CEP, telefone e URL, além da validação e preparação dos
arquivos enviados.

Usuários
~~~~~~~~

O usuário autenticado é associado às operações de criação, atualização e
exclusão. O envio de anexos também valida a existência do usuário responsável.

Storage privado
~~~~~~~~~~~~~~~

O conteúdo dos anexos é armazenado no storage privado configurado pela
aplicação. O banco de dados mantém os metadados e a referência ao arquivo.

Permissões e acesso
-------------------

Todas as operações utilizam a autenticação JWT e exigem usuário autenticado,
conforme a configuração global do Django REST Framework.

Auditoria
---------

Na criação, o usuário autenticado é registrado na empresa, nos responsáveis
técnicos e nos anexos enviados.

Na atualização, o usuário é registrado como responsável pela alteração da
empresa e dos responsáveis atualizados.

Na exclusão lógica, o usuário e a data da operação são registrados na empresa
e nos responsáveis técnicos removidos.

As respostas de consulta apresentam os
nomes dos usuários e as datas de criação e atualização.

Estados e transições
--------------------

A empresa possui dois estados representados pelo campo ``status``:

* ativa;
* inativa.

Quando o status não é informado no cadastro, a empresa inicia ativa. O
cadastro e a atualização permitem definir explicitamente qualquer um dos dois
estados.

Regras de Negócio
=================

Esta seção apresenta as regras de negócio que orientam o funcionamento do
domínio **Empresa**.

As regras descrevem comportamentos, restrições, validações e condições que
precisam ser respeitados pelas funcionalidades do domínio.

.. toctree::
   :maxdepth: 1

   regras_negocio

Documentação do código
======================

Esta seção apresenta a documentação técnica dos componentes que implementam o
domínio **Empresa**.

A documentação é gerada automaticamente a partir dos módulos Python do app e
tem como objetivo facilitar a compreensão da implementação e de suas
responsabilidades técnicas.

.. toctree::
   :maxdepth: 1

   codigo/index
