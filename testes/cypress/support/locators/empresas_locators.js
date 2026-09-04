class Empresas_Localizadores {

  // criar
  menu_cadastro = () => '.p-1 > .cursor-pointer'
  menu_empresas = () => '[href="/empresas"]'
  btn_cadastrar_empresa = () => 'div.flex.items-center.justify-between > a'
  campo_nome = () => '#nome'
  campo_cnpj = () => '#cnpj'
  campo_razao_social = () => '#razao_social'
  select_status = () => '#status'
  link_rastreio = () => '#link_rastreio'
  campo_cep = () => '#cep'
  campo_logradouro = () => '#logradouro'
  campo_numero = () => '#numero'
  campo_complemento = () => '#complemento'
  campo_cidade = () => '#cidade'
  campo_estado = () => '#estado'
  btn_salvar_cadastro = () => 'div.justify-between > .flex > .bg-primary'
  tipo_responsavel_tecnico = () => '#responsaveis_tecnicos\\.0\\.tipo'
  campo_nome_responsavel_tecnico = () => '#responsaveis_tecnicos\\.0\\.nome'
  campo_telefone_responsavel_tecnico = () => '#responsaveis_tecnicos\\.0\\.telefone'
  campo_email_responsavel_tecnico = () => '#responsaveis_tecnicos\\.0\\.email'
  campo_numero_crea_responsavel_tecnico = () => '#responsaveis_tecnicos\\.0\\.numero_crea'
  campo_numero_art_responsavel_tecnico = () => '#responsaveis_tecnicos\\.0\\.numero_art'
  documento_responsavel_tecnico = () => '.space-y-1.col-span-3 > div.flex > .group\\/button'

  // consultar
  btn_abrir_empresa = () => ':nth-child(1) > .py-2 > .group\\/button'
  btn_rastrear_empresa = () => ':nth-child(1) > :nth-child(5) > .font-medium'
  btn_limpar_filtros = () => '.justify-end > :nth-child(1)'
  btn_buscar = () => '.justify-end > :nth-child(2)'

}

export default Empresas_Localizadores 