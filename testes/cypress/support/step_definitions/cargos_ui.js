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

Quando('clico para excluir o cadastro de cargo  de profissionais {string}', function () {
  cy.nao_excluir_cargo()
})

Então('o sistema não exclui cargo vinculado', function () { 
  cy.validar_cargo_nao_excluido()
})