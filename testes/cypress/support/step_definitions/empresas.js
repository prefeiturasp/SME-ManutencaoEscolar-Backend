import { When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Quando = When
const Então = Then


Quando('acesso a tela Empresas', function () {
  cy.acessar_empresas() 
})

Quando('crio cadastro de empresa {string}', function () {
  cy.criar_empresa()   
})

Então('o sistema salva a empresa', function () { 
  cy.validar_cadastro_empresa()
})
