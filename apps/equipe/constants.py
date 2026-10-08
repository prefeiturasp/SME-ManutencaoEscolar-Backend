"""Constantes do domínio Equipe."""


class EquipeErrorMessages:
    """Mensagens de erro das regras de equipe."""

    NOME_EQUIPE_DUPLICADO_TITULO = "Já existe uma equipe com este nome!"
    NOME_EQUIPE_DUPLICADO = (
        "Já existe uma equipe com o nome {nome_equipe} cadastrada na empresa "
        "{nome_empresa}. Para cadastrar uma nova equipe, informe um nome "
        "diferente."
    )
    PROFISSIONAL_OBRIGATORIO = (
        "Informe pelo menos um profissional para a equipe."
    )
    PROFISSIONAL_DUPLICADO = (
        "Não é permitido informar o mesmo profissional mais de uma vez."
    )
    PROFISSIONAL_INATIVO = (
        "Não é permitido vincular um profissional inativo à equipe."
    )
    PROFISSIONAL_OUTRA_EQUIPE_TITULO = (
        "Profissional já vinculado a uma equipe!"
    )
    PROFISSIONAL_OUTRA_EQUIPE = (
        "O profissional {nome_profissional} já possui vínculo "
        "com a equipe {nome_equipe}. Para incluir esse registro, "
        "primeiro remova o vínculo atual com a equipe."
    )
    PROFISSIONAIS_OUTRA_EQUIPE_TITULO = (
        "Profissionais já vinculados a uma ou mais equipes!"
    )
    PROFISSIONAIS_OUTRA_EQUIPE = (
        "Mais de um profissional já possui vínculo com uma ou mais equipes. "
        "Para incluir esse registro, primeiro remova os vínculos atuais."
    )
    FUNCAO_INVALIDA = (
        "A função informada não pertence ao profissional selecionado."
    )
    EMPRESA_LOTE_INVALIDA = (
        "A empresa informada não está associada ao lote selecionado."
    )
