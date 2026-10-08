import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Quando = When
const Então = Then


Quando('acesso a tela Serviços', function () {
  cy.acessar_servicos() 
})

Quando('crio cadastro de serviço {string}', function () {
  cy.criar_servico()   
})

Então('o sistema salva o serviço', function () { 
  cy.validar_cadastro_servico()
})

Quando('não preencho o cadastro de serviço {string}', function () {
  cy.clicar_cadastrar_servico() 
})

Então('o sistema não cadastra o serviço sem campos obrigatórios', function () { 
  cy.validar_campos_preenchidos_servico()
})

Quando('cancelo preenchimento o cadastro de serviço {string}', function () {
  cy.clicar_cancelar_cadastro_servico() 
})

Então('o sistema não cadastra o serviço retornando para listagem', function () { 
  cy.validar_cancelar_cadastro_servico()
})

Então('o sistema informa serviço já cadastrado', function () { 
  cy.validar_cadastro_servico_duplicado()
})

Quando('cancelo a exclusão do cadastro de serviço {string}', function () {
  cy.cancelar_exclusao_servico()
})

Então('o sistema não exclui o serviço retornando para os detalhes', function () { 
  cy.validar_editar_servico()
})

Quando('aciono a exclusão do cadastro de serviço {string}', function () {
})

Quando('fecho o modal de exclusão do serviço', function () {
  cy.acionar_exclusao_servico()
})

Quando('clico para excluir o cadastro de serviço {string}', function () {
  cy.excluir_servico()
})

Então('o sistema exclui o serviço', function () { 
  cy.validar_exclusao_servico()
})

Quando('edito o cadastro de serviço {string}', function () {
  cy.editar_servico()   
})

Então('o sistema salva a edição do serviço', function () { 
  cy.validar_edicao_servico() 
})

Quando('cancelo edição do cadastro de serviço {string}', function () {
  cy.cancelar_edicao_servico()   
})

Então('o sistema não edita o serviço retornando para listagem', function () {
  cy.validar_cancelar_cadastro_servico() 
})

Quando('insiro os mesmos dados do serviço {string}', function () { 
  cy.editar_servico_existente 
})

Então('o sistema informa serviço ao tentar salvar o serviço', function () {
  cy.validar_cadastro_servico_duplicado() 
})