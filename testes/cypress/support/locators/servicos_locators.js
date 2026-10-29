class Servicos_Localizadores {

  // criar
  menu_cadastro = () => '.p-1 > .cursor-pointer'
  menu_servicos = () => '[href="/servicos"]'
  btn_cadastrar_servicos = () => 'div.justify-between > .group\\/button'
  campo_nome = () => '#nome'  
  select_status = () => '#status' 
  opcoes_status = () => '[role="option"]' 
  btn_cancelar = () => 'a[href="/servicos"]:contains("Cancelar")'
  btn_salvar_cadastro = () => 'div.justify-between > .flex > .bg-primary'

  // consultar
  tbl_nome = () => 'tbody > tr > :nth-child(1)'
  tbl_status = () => 'tbody > tr > :nth-child(2)'
  btn_limpar_filtro = () => 'button:contains("Limpar filtro")'

  // editar
  btn_buscar_servico = () => 'button[class*="max-w-[165px]"]'
  btn_editar_servico = () => 'button[aria-label="Editar Teste automação"]'
  btn_cancelar_detalhes_servico = () => 'a[href="/servicos"]'

  // excluir
  btn_excluir_servico = () => 'button:contains("Excluir serviço")'
  btn_confirmar_exclusao = () => 'button[data-slot="alert-dialog-action"]:contains("Excluir serviço")'
  btn_cancelar_exclusao = () => 'button[data-slot="alert-dialog-cancel"]:contains("Cancelar")'
  btn_fechar_exclusao = () => 'button[data-slot="alert-dialog-cancel"]'

}

export default Servicos_Localizadores 