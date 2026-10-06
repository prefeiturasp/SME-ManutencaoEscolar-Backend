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
  cy.clicar_cancelar_cadastro() 
})

Então('o sistema não cadastra o serviço retornando para listagem', function () { 
  cy.validar_cancelar_cadastro()
})

Então('o sistema informa serviço já cadastrado', function () { 
  cy.validar_cadastro_servico_duplicado()
})

