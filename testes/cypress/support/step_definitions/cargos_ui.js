import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Quando = When
const Então = Then


Quando('acesso a tela Cargos', function () {
  cy.acessar_cargos() 
})

Quando('crio cadastro de cargo {string}', function () {
  cy.criar_cargo()   
})

Então('o sistema salva o cargo', function () { 
  cy.validar_cadastro_cargo()
})

Quando('não preencho o cadastro de cargo {string}', function () {
  cy.clicar_cadastrar_cargo() 
})

Então('o sistema não cadastra o cargo sem campos obrigatórios', function () { 
  cy.validar_campos_preenchidos_cargo()
})

Quando('preencho sim em documento de cargo {string}', function () {
  cy.inserir_documento()
})

Então('o sistema permite inserir no cargo documentos exigidos', function () {
  cy.validar_campos_preenchidos_documento() 
})

Quando('cancelo preenchimento o cadastro de cargo {string}', function () {
  cy.clicar_cancelar_cadastro_cargo() 
})

Então('o sistema não cadastra o cargo retornando para listagem', function () { 
  cy.validar_cancelar_cadastro_cargo()
})

Então('o sistema informa cargo já cadastrado', function () { 
  cy.validar_cadastro_cargo_duplicado()
})

Quando('cancelo a exclusão do cadastro de cargo {string}', function () {
  cy.cancelar_exclusao_cargo()
})

Então('o sistema não exclui o cargo retornando para os detalhes', function () { 
  cy.validar_editar_cargo()
})

Quando('aciono a exclusão do cadastro de cargo {string}', function () {
})

Quando('fecho o modal de exclusão do cargo', function () {
  cy.acionar_exclusao_cargo()
})

Quando('clico para excluir o cadastro de cargo {string}', function () {
  cy.excluir_cargo()
})

Então('o sistema exclui o cargo', function () { 
  cy.validar_exclusao_cargo()
})

Quando('edito o cadastro de cargo {string}', function () {
  cy.editar_cargo()   
})

Então('o sistema salva a edição do cargo', function () { 
  cy.validar_edicao_cargo() 
})

Quando('apago o preenchimento no cadastro de cargo {string}', function () {
  cy.editar_campos_cargo()  
})

Então('o sistema campos obrigatórios salva a edição do cargo', function () {
  cy.validar_campos_obrigatorios_cargo() 
})

Quando('cancelo edição do cadastro de cargo {string}', function () {
  cy.cancelar_edicao_cargo()   
})

Então('o sistema não edita o cargo retornando para listagem', function () {
  cy.validar_cancelar_cadastro_cargo() 
})

Quando('insiro os mesmos dados do cargo {string}', function () { 
  cy.editar_cargo_existente()
})

Quando('filtro o nome do cargo {string}', function () {
  cy.filtrar_nome_cargo()  
})

Então('o sistema retorna o cargo', function () {
  cy.validar_filtro_nome_cargo()  
})

Quando('filtro o status do cargo {string}', function () {
  cy.filtrar_status_cargo()  
})

Então('o sistema retorna o cargo ativo', function () {
  cy.validar_filtro_status_cargo()  
})

Quando('cancelo o filtro de cargo {string}', function () {
  cy.limpar_filtro_cargo()  
})

Então('o sistema retorna todos cargos na listagem', function () {
  cy.validar_filtro_vazio_cargo() 
})

Quando('clico no cadastro de cargo {string}', function () {
  cy.consultar_detalhes_cargo()  
})

Então('o sistema exibe os detalhes do cargo', function () {
  cy.validar_editar_cargo()  
})

Quando('filtro dados do cargo inexistente', function () {
  cy.filtrar_cargo_inexistente()  
})

Então('o sistema informa que cargo não foi encontrado', function () {
  cy.validar_filtro_cargo_inexistente()  
})