====
Core
====

Visão Geral
===========

O domínio **Core** é responsável por fornecer funcionalidades utilizadas pelos demais domínios da aplicação.

Seu objetivo é centralizar serviços relacionados à autenticação e autorização,
integração com sistemas externos, gerenciamento de arquivos, auditoria,
comunicação assíncrona e funcionalidades comuns aos demais módulos.

O Core não representa um domínio de negócio específico. Ele fornece
infraestrutura e serviços compartilhados que garantem comportamento
consistente entre os diferentes módulos da aplicação.

Responsabilidades
-----------------

As principais responsabilidades do Core são:

- autenticação de usuários;
- gerenciamento de tokens JWT;
- controle de sessão e logout;
- recuperação e alteração de senha;
- integração com o EOL/CoreSSO;
- sincronização dos dados do usuário;
- armazenamento de arquivos em storage privado;
- envio assíncrono de e-mails;
- auditoria dos registros;
- exclusão lógica e restauração de registros;
- disponibilização de funcionalidades e componentes reutilizáveis.

Arquitetura funcional
---------------------

A estrutura funcional do Core pode ser representada da seguinte forma::

    Core
    |
    +-- Autenticação
    |   +-- Login
    |   +-- JWT Access Token
    |   +-- JWT Refresh Token
    |   +-- Renovação de sessão
    |   +-- Logout
    |   +-- Recuperação de senha
    |   +-- Alteração de senha
    |
    +-- Integrações
    |   +-- EOL
    |   +-- CoreSSO
    |   +-- Consulta de usuário
    |   +-- Consulta de cargo
    |   +-- Alteração de senha
    |
    +-- Arquivos
    |   +-- Upload
    |   +-- Validação
    |   +-- Metadados
    |   +-- Storage privado
    |
    +-- Comunicação
    |   +-- E-mail
    |   +-- Celery
    |   +-- Retry de tarefas
    |
    +-- Persistência
        +-- UUID
        +-- Auditoria
        +-- Soft Delete
        +-- Restauração

Autenticação
------------

O Core é responsável pelo fluxo de autenticação da aplicação.

O usuário pode realizar login utilizando seu Registro Funcional (RF) ou CPF.
As credenciais são validadas através da integração com o EOL/CoreSSO.

Após uma autenticação bem-sucedida, o Core obtém os dados complementares do
usuário, sincroniza as informações necessárias localmente e disponibiliza os
tokens utilizados pela aplicação.

O fluxo geral é::

    Cliente
       |
       v
    Login
       |
       v
    Core
       |
       v
    EOL/CoreSSO
       |
       +-- Autenticação
       +-- Consulta do usuário
       +-- Consulta do cargo
       |
       v
    Sincronização local
       |
       v
    Access Token + Refresh Token

Sessão
------

A autenticação utiliza JWT para representar a sessão do usuário.

O ``access token`` é utilizado para acesso aos recursos protegidos da API.

O ``refresh token`` permite solicitar uma nova sessão sem que o usuário
precise informar novamente suas credenciais.

O Core também controla a revogação dos refresh tokens, impedindo que tokens
revogados sejam utilizados posteriormente.

Recuperação de senha
--------------------

O Core disponibiliza o fluxo de recuperação de senha integrado ao
CoreSSO.

O usuário informa seu RF ou CPF e, quando os dados necessários estão
disponíveis, o sistema gera um token de recuperação e envia um e-mail de
forma assíncrona.

O link recebido permite que o usuário informe uma nova senha.

A alteração efetiva da senha é realizada através da integração com o
CoreSSO.

Arquivos e anexos
-----------------

O Core fornece uma estrutura comum para gerenciamento de arquivos anexados
aos registros da aplicação.

Os arquivos recebidos são validados antes do armazenamento. São verificadas
características como:

* existência do arquivo;
* nome;
* tamanho;
* extensão;
* tipo MIME.

Os metadados do arquivo são persistidos no banco de dados, enquanto o
conteúdo é armazenado em storage privado.

Atualmente, o storage utilizado é o MinIO.

O nome original do arquivo é preservado como informação de negócio, mas o
nome físico utilizado no storage é gerado pelo sistema através de UUID.

Auditoria
---------

Os modelos que utilizam a estrutura base do Core possuem informações de
auditoria.

São registrados, quando aplicável:

* usuário responsável pela criação;
* data e hora da criação;
* usuário responsável pela última alteração;
* data e hora da última alteração;
* usuário responsável pela exclusão;
* data e hora da exclusão.

Identificação
-------------

Os registros possuem um UUID gerado automaticamente pelo sistema.

O UUID é utilizado como identificador dos registros expostos pela aplicação
e não deve ser alterado manualmente.

Exclusão lógica
---------------

O Core utiliza exclusão lógica para preservar os registros no banco de
dados.

Ao excluir um registro, o sistema registra a data e o usuário responsável
pela operação, sem remover fisicamente o registro.

As consultas padrão retornam somente registros que não foram excluídos.

Quando necessário, registros excluídos podem ser consultados através do
gerenciador apropriado e restaurados.

Comunicação assíncrona
----------------------

Operações que não precisam ser executadas dentro do ciclo da requisição HTTP
podem ser processadas de forma assíncrona.

O envio de e-mails utiliza Celery, permitindo que a aplicação continue o
processamento da requisição sem aguardar a conclusão da comunicação com o
servidor de e-mail.

As tarefas assíncronas possuem mecanismo de nova tentativa para lidar com
falhas transitórias.

Health Check
------------

O Core disponibiliza um endpoint público de health check.

O endpoint permite que mecanismos de infraestrutura verifiquem se a
aplicação está respondendo corretamente.


Regras de Negócio
=================

Esta seção apresenta as regras de negócio que orientam o
funcionamento do domínio **Core**.

As regras descrevem comportamentos, restrições, validações
e condições que precisam ser respeitados pelas funcionalidades
do domínio.

.. toctree::
   :maxdepth: 1

   regras_negocio

Documentação do código
======================

Esta seção apresenta a documentação técnica dos componentes que
implementam o domínio **Core**.

A documentação é gerada automaticamente a partir dos módulos
Python do app e tem como objetivo facilitar a compreensão da
implementação e de suas responsabilidades técnicas.

.. toctree::
   :maxdepth: 1

   codigo/index
