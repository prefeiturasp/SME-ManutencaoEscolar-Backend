import Servicos_Localizadores from '../locators/servicos_locators'

const servicos_localizadores = new Servicos_Localizadores()

Cypress.Commands.add('acessar_servicos', () => { 
  cy.get(servicos_localizadores.menu_cadastro())
    .should('exist')
    .click()

  cy.get(servicos_localizadores.menu_servicos())
    .should('be.visible')
    .click()

  cy.url({ timeout: 10000 }).should('include', 'servicos')
})

Cypress.Commands.add('criar_servico', () => {  
  cy.get(servicos_localizadores.btn_cadastrar_servicos())
    .should('be.visible')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/servicos/cadastrar')

  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.opcoes_status())
    .should('be.visible')
    .contains('Ativo')
    .click()

  cy.get(servicos_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cadastro_servico', () => {
  cy.contains('O serviço foi cadastrado.')
})

Cypress.Commands.add('clicar_cadastrar_servico', () => {  
  cy.get(servicos_localizadores.btn_cadastrar_servicos())
    .should('be.visible')
    .click() 
})

Cypress.Commands.add('validar_campos_preenchidos_servico', () => {
  cy.get(servicos_localizadores.btn_salvar_cadastro())
    .should('not.exist')
})

Cypress.Commands.add('clicar_cancelar_cadastro_servico', () => {
  cy.get(servicos_localizadores.btn_cadastrar_servicos())
    .should('be.visible')
    .click() 
     
  cy.get(servicos_localizadores.btn_cancelar())
    .should('be.visible')
    .click() 
})

Cypress.Commands.add('validar_cancelar_cadastro_servico', () => {
  cy.get(servicos_localizadores.btn_cadastrar_servicos())
    .should('be.visible')
})

Cypress.Commands.add('validar_cadastro_servico_duplicado', () => {
  cy.contains('Já existe um serviço com este nome cadastrado no sistema.')
})

Cypress.Commands.add('cancelar_exclusao_servico', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_excluir_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_cancelar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_editar_servico', () => {
  cy.url({ timeout: 10000 }).should('include', '/editar')
})

Cypress.Commands.add('acionar_exclusao_servico', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_excluir_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_cancelar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('excluir_servico', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible') 
    .click()

  cy.get(servicos_localizadores.btn_excluir_servico())
    .should('be.visible')
    .click()
  
  cy.get(servicos_localizadores.btn_confirmar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_exclusao_servico', () => {
  cy.contains('O serviço foi excluído.')  
})

Cypress.Commands.add('editar_servico', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible')
    .click()

  cy.url().should('include', '/servicos/').and('include', '/editar')

  cy.get(servicos_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.opcoes_status())
    .contains('Inativo')
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_edicao_servico', () => {
  cy.contains('As alterações foram salvas.')  
})

Cypress.Commands.add('cancelar_edicao_servico', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible')
    .click()

  cy.url().should('include', '/servicos/').and('include', '/editar')

  cy.get(servicos_localizadores.btn_cancelar())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('editar_servico_existente', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible') 
    .click()

  cy.url().should('include', '/servicos/').and('include', '/editar')

  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .clear()
	
	cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste serviço')

  cy.get(servicos_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('editar_campos_servico', () => {
  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(servicos_localizadores.btn_buscar_servico())
    .should('be.visible')
    .click()

  cy.get(servicos_localizadores.btn_editar_servico())
    .should('be.visible')
    .click()

  cy.url().should('include', '/servicos/').and('include', '/editar')

  cy.get(servicos_localizadores.campo_nome())
    .should('be.visible')
    .clear()
})

Cypress.Commands.add('validar_campos_obrigatorios_servico', () => {
  cy.contains('Campo obrigatório')  
})
