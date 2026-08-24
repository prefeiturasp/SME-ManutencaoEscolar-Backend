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

Quando('clico em criar cadastro de empresa {string}', function () {
  cy.clicar_criar_empresa()
})

Então('o sistema não salva a empresa sem preenchimento dos campos', function () { 
  cy.validar_cadastro_nao_preenchido_empresa()  
})

Quando('crio cadastro a empresa {string}', function () {
  cy.criar_empresa_inativa()   
})

Então('o sistema salva a empresa inativa', function () { 
  cy.validar_cadastro_empresa()
})

Quando('valido o campo obrigatório {string}', (campo) => {
  cy.campos_obrigatorios_criar_empresa(campo)
})

Então('o sistema exibe mensagem de campo obrigatório', () => {
  cy.validar_campo_obrigatorio_empresa()
})