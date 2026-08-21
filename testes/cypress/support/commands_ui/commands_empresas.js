import Empresas_Localizadores from '../locators/empresas_locators'
import { faker } from '@faker-js/faker'

const empresas_localizadores = new Empresas_Localizadores()
const cnpjEmpresa = faker.string.numeric(14)

Cypress.Commands.add('acessar_empresas', () => { 
  cy.get(empresas_localizadores.menu_cadastro())
    .should('exist')
    .click()

  cy.get(empresas_localizadores.menu_empresas())
    .should('be.visible')
    .click()

  cy.url({ timeout: 10000 }).should('include', 'cadastro/empresas')
})

Cypress.Commands.add('criar_empresa', () => {
  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/cadastro/empresas/cadastrar')

  cy.get(empresas_localizadores.campo_nome())
    .should('be.visible')
    .type(Cypress.env('NOME_EMPRESA'))

  cy.get(empresas_localizadores.campo_cnpj())
    .should('be.visible')
    .type(cnpjEmpresa)

  cy.get(empresas_localizadores.campo_razao_social())
    .should('be.visible')
    .type(Cypress.env('RAZAO_SOCIAL'))

  cy.get(empresas_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.contains('Ativo')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.link_rastreio())
    .should('be.visible')
    .type(Cypress.env('LINK_RASTREIO'))

  cy.get(empresas_localizadores.campo_cep())
    .should('be.visible')
    .type(Cypress.env('CEP'))
    
  cy.get(empresas_localizadores.campo_logradouro())
    .should('be.visible')
    .type(Cypress.env('LOGRADOURO'))
    
  cy.get(empresas_localizadores.campo_numero())
    .should('be.visible')
    .type(Cypress.env('NUMERO'))
    
  cy.get(empresas_localizadores.campo_complemento())
    .should('be.visible')
    .type(Cypress.env('COMPLEMENTO'))  

  cy.get(empresas_localizadores.campo_cidade())
    .should('be.visible')
    .type(Cypress.env('CIDADE'))    

  cy.get(empresas_localizadores.campo_estado())
    .should('be.visible')
    .type(Cypress.env('ESTADO'))

  cy.contains('SP')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cadastro_empresa', () => {
  cy.contains('Sucesso')
})