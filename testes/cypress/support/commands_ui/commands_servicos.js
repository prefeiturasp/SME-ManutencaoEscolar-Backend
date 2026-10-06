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
    .should('be.disabled')
})

Cypress.Commands.add('clicar_cancelar_cadastro', () => {
  cy.get(servicos_localizadores.btn_cadastrar_servicos())
    .should('be.visible')
    .click() 
     
  cy.get(servicos_localizadores.btn_cancelar())
    .should('be.visible')
    .click() 
})

Cypress.Commands.add('validar_cancelar_cadastro', () => {
  cy.get(servicos_localizadores.btn_cadastrar_servicos())
    .should('be.visible')
})

Cypress.Commands.add('validar_cadastro_servico_duplicado', () => {
  cy.contains('Já existe um serviço com este nome cadastrado no sistema.')
})
