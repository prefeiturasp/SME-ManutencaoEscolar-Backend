import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Dado = Given
const Quando = When
const Então = Then

// Realiza a autenticação com sucesso
Dado('que acesso o endpoint de autenticação', function () {  
})

Quando('envio os dados de acesso', function () { 
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + `/api/v1/login/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: {
      login: `${Cypress.env('LOGIN_ADMIN')}`,
      senha: `${Cypress.env('SENHA_ADMIN')}`
    },
    failOnStatusCode: false
  }).as('response')
})

Então('retorna status 200 com o token válido', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
  })
})

// Login deve ser obrigatório
Quando('envio os dados sem o login', function () { 
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + `/api/v1/login/`,
    headers: {
      accept: 'application/json',
      'content-type': 'application/json',
    },
    body: {
      login:" ",
      senha: `${Cypress.env('SENHA')}`
    },
    failOnStatusCode: false
  }).as('response')
})

Então('retorna status 400 que acesso foi inválido', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400)

    expect(response.body)
      .to.have.property('login')
      .and.to.be.an('array')

    expect(response.body.login)
      .to.include('Este campo pode não estar em branco.')    
  })
})

// Senha deve ser obrigatória
Quando('envio os dados sem a senha', function () { 
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + `/api/v1/login/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: {
      login: `${Cypress.env('LOGIN_DIRETOR')}`,
      senha:" "
    },
    failOnStatusCode: false
  }).as('response')
})

Então('retorna status 400 que é necessário ser informada', function () {
  cy.get('@response').then((response) => {  
    expect(response.status).to.eq(400)

    expect(response.body)
      .to.have.property('senha')
      .and.to.be.an('array')

    expect(response.body.senha)
      .to.include('Este campo pode não estar em branco.')
  })
})

// Não autenticar com usuário inválido
Quando('envio os dados com usuário inválido', function () { 
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + `/api/v1/login/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: {
      login: `${Cypress.env('LOGIN_INVALIDO')}`,
      senha: `${Cypress.env('SENHA')}`
    },
    failOnStatusCode: false
  }).as('response')
})

Então('retorna status 401 retorna sem acessar com usuário', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)

    expect(response.body)
      .to.have.property('detail')
      .and.to.eq('Usuário e/ou senha inválida')  
  })
})

// Não autenticar com senha inválida
Quando('envio os dados com senha inválida', function () { 
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + `/api/v1/login/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: {
      login: `${Cypress.env('LOGIN_DIRETOR')}`,
      senha: `${Cypress.env('SENHA_INVALIDA')}`
    },
    failOnStatusCode: false
  }).as('response')
})

Então('retorna status 401 retorna sem acessar com senha', function () {
  cy.get('@response').then((response) => {
  
    expect(response.status).to.eq(401)

    expect(response.body)
      .to.have.property('detail')
      .and.to.eq('Usuário e/ou senha inválida')
  })
})