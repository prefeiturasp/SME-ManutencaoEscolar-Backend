class Servicos_Localizadores {

  // criar
  menu_cadastro = () => '.p-1 > .cursor-pointer'
  menu_servicos = () => '[href="/servicos"]'
  btn_cadastrar_servicos = () => 'div.justify-between > .group\\/button'
  campo_nome = () => '#nome'  
  select_status = () => '#status' 
  opcoes_status = () => '[role="option"]' 
  btn_cancelar = () => 'div.items-center > div.flex > .flex > .group\\/button'
  btn_salvar_cadastro = () => 'div.justify-between > .flex > .bg-primary'

  // editar
  btn_buscar_servico = () => 'button[class*="max-w-[165px]"]'
  btn_editar_servico = () => 'button[aria-label="Editar Teste automação"]'
  btn_cancelar_detalhes_servico = () => 'a[href="/servicos"]'
  btn_detalhes_servico = () => 'div.items-center > div.flex > .flex > .group\\/button'

  // excluir
  btn_excluir_servico = () => 'button:contains("Excluir serviço")'
  btn_confirmar_exclusao = () => 'button[data-slot="alert-dialog-action"]:contains("Excluir serviço")'
  btn_cancelar_exclusao = () => 'button[data-slot="alert-dialog-cancel"]:contains("Cancelar")'
   btn_fechar_exclusao = () => 'button[data-slot="alert-dialog-cancel"]'

}

export default Servicos_Localizadores 