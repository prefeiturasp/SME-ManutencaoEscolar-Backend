class Cargos_Localizadores {

  // criar
  menu_cadastro = () => '.p-1 > .cursor-pointer'
  menu_cargos = () => '[href="/cargos"]'
  btn_cadastrar_cargos = () => 'div.justify-between > .group\\/button'
  campo_nome = () => '#nome'  
  select_documento = () => '#exige_documento' 
  opcoes_documento = () => '[role="option"]'
  campo_nome_documento = () => '#novo_documento'  
  btn_cancelar = () => 'a[href="/cargos"]:contains("Cancelar")'
  btn_salvar_cadastro = () => 'div.justify-between > .flex > .bg-primary'

  // consultar
  tbl_nome = () => 'tbody > tr > :nth-child(1)'
  tbl_documento = () => 'tbody > tr > :nth-child(2)'
  btn_limpar_filtro = () => 'button:contains("Limpar filtro")'

  // editar
  btn_buscar_cargo = () => 'button[class*="max-w-[165px]"]'
  btn_editar_cargo = () => 'button[aria-label="Editar Teste automação"]'
  btn_editar_cargo_permanente = () => 'button[aria-label="Editar Pintor"]'
  btn_cancelar_detalhes_cargo = () => 'a[href="/cargos"]'

  // excluir
  btn_excluir_cargo = () => 'button:contains("Excluir cargo")'
  btn_confirmar_exclusao = () => 'button[data-slot="alert-dialog-action"]:contains("Excluir cargo")'
  btn_cancelar_exclusao = () => 'button[data-slot="alert-dialog-cancel"]:contains("Cancelar")'
  btn_fechar_exclusao = () => 'button[data-slot="alert-dialog-cancel"]'

}

export default Cargos_Localizadores 