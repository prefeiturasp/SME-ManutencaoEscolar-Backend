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

Quando('valido o campo obrigatório {string} na empresa', (campo) => {
  cy.campos_obrigatorios_criar_empresa(campo)
})

Então('o sistema exibe campo obrigatório de empresa', () => {
  cy.validar_campo_obrigatorio_empresa()
})

Quando('clico no cadastro de empresa {string}', () => {
  cy.abrir_cadastro_empresa()
})

Então('o sistema exibe os detalhes da empresa', () => {
  cy.validar_consulta_empresa()
})

Quando('clico no rastrear empresa {string}', () => {
  cy.rastrear_empresa()
})

Então('o sistema direciona ao rastreio da empresa', () => {
  cy.validar_consulta_empresa()
})

Quando('clico limpar filtros de empresa', () => {
  cy.limpar_filtros_empresa()
})

Então('o sistema retorna a listagem de empresas', () => {
  cy.validar_filtros_empresa()
})

Quando('filtro por {string} na empresa', (campo) => {
  cy.filtros_consulta_empresa(campo)
})

Então('o sistema busca por {string} o cadastro de emrpesa', () => {
  cy.validar_filtros_empresa()
})

Quando('filtro por {string} inexistente na empresa', (campo) => {
  cy.filtros_sem_dados_empresa(campo)
})

Então('o sistema não busca por {string} no cadastro de emrpesa', () => {
  cy.validar_dados_nao_encontrados_empresa()
})