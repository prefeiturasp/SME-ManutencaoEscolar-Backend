Esta seção documenta as regras de negócio que orientam o funcionamento do domínio **Lote**.

Cadastro
--------

Todo lote deve possuir nome, código de cadastro e uma empresa válida.

O nome e o código de cadastro de um lote devem possuir, no máximo, 255
caracteres.

No cadastro, os espaços localizados no início e no final do nome e do código
de cadastro devem ser removidos antes da persistência.



Quando o status não for informado no cadastro, o lote deve ser criado como
ativo.



O período inicial e o período final são opcionais.



Quando os dois limites do período forem informados, o período final não pode
ser anterior ao período inicial.



A empresa informada no cadastro ou na atualização deve corresponder a uma
empresa existente.

Vínculos com Diretorias Regionais
---------------------------------



Todas as DREs informadas devem corresponder a registros existentes.



Uma mesma DRE não pode aparecer mais de uma vez na lista enviada em uma
operação de cadastro ou atualização.



Uma DRE associada a um lote ativo e não excluído não pode ser vinculada a
outro lote.



O vínculo de uma DRE com um lote inativo não impede que ela seja vinculada a
outro lote.



O vínculo de uma DRE com um lote excluído logicamente não impede que ela seja
vinculada a outro lote.



Na atualização, os vínculos do próprio lote devem ser desconsiderados durante
a verificação de disponibilidade das DREs.



Quando uma lista não vazia de DREs for informada na atualização, devem
permanecer vinculadas somente as DREs contidas nessa lista.



Quando o cadastro ou a atualização for rejeitado por conflito de DRE, a
resposta deve identificar as DREs indisponíveis e os códigos dos lotes ativos
aos quais elas estão associadas.

Consulta
--------



A consulta por código de cadastro ou nome deve aceitar correspondência
parcial sem diferenciar letras maiúsculas de minúsculas.



A consulta por situação deve permitir a seleção de lotes ativos ou inativos.



Quando o filtro de período inicial for utilizado, devem ser retornados
somente lotes cuja data inicial seja igual ou posterior à data informada.



Quando o filtro de período final for utilizado, devem ser retornados somente
lotes cuja data final seja igual ou anterior à data informada.



Quando múltiplas DREs forem informadas no filtro, cada lote correspondente
deve aparecer apenas uma vez no resultado.



A ordenação padrão deve apresentar lotes ativos antes dos inativos e, dentro
dessa ordenação, os registros mais recentes por identificador primeiro.

Atualização
-----------



A atualização de um lote deve registrar o usuário responsável pela operação.



A alteração do status pode tornar um lote ativo ou inativo.

Validade
--------



Um lote ativo deve ser inativado automaticamente quando seu período final for
anterior à data local da execução da verificação.



Um lote cujo período final seja igual à data da verificação não deve ser
inativado nessa execução.



Lotes já inativos ou excluídos logicamente não devem ser processados pela
inativação automática.

Auditoria e exclusão
--------------------



A criação de um lote deve registrar o usuário responsável pela criação e pela
última atualização.



A exclusão de um lote deve ser lógica e deve registrar o usuário responsável
pela operação.



As operações de criação, atualização e exclusão somente podem ser executadas
quando o usuário da requisição for reconhecido como usuário da aplicação.

Integridade referencial
-----------------------



Uma empresa associada a um lote não pode ser fisicamente excluída enquanto
o lote mantiver essa associação.



Uma DRE não pode ser fisicamente excluída enquanto existir um vínculo que a
referencie.
