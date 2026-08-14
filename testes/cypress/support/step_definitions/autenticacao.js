import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

// Realiza a autenticação com sucesso
Given('que acesso o endpoint de autenticação', function () {  
})

When('envio os dados de acesso', function () { 
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + `/api/v1/login/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: {
      login: `${Cypress.env('LOGIN_DIRETOR')}`,
      senha: `${Cypress.env('SENHA')}`
    },
    failOnStatusCode: false
  }).as('response')
})

Then('retorna status 200 com o token válido', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('refresh').and.to.be.a('string').and.not.be.empty
    expect(response.body).to.have.property('access').and.to.be.a('string').and.not.be.empty

    expect(response.body).to.have.property('usuario').and.to.be.an('object')

    expect(response.body.usuario).to.have.property('id')
    expect(response.body.usuario).to.have.property('uuid').and.to.be.a('string')
    expect(response.body.usuario).to.have.property('nome').and.to.be.a('string')
    expect(response.body.usuario).to.have.property('email').and.to.be.a('string')
    expect(response.body.usuario).to.have.property('registro_funcional').and.to.be.a('string')
    expect(response.body.usuario).to.have.property('username').and.to.be.a('string')

    expect(response.body.usuario).to.have.property('perfil_acesso').and.to.be.an('object')

    expect(response.body.usuario.perfil_acesso)
      .to.have.property('cargo')
      .and.to.be.a('string')

    expect(response.body.usuario.perfil_acesso)
      .to.have.property('perfil')
      .and.to.be.an('object')

    expect(response.body.usuario.perfil_acesso.perfil)
      .to.have.property('codigo')
      .and.to.be.a('string')

    expect(response.body.usuario.perfil_acesso.perfil)
      .to.have.property('descricao')
      .and.to.be.a('string')

    expect(response.body.usuario)
      .to.have.property('diretoria_regional')
      .and.to.be.a('string')

    expect(response.body.usuario)
      .to.have.property('unidade_educacional')
      .and.to.be.a('string')
  })
})

// Login deve ser obrigatório
When('envio os dados sem o login', function () { 
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

Then('retorna status 400 que acesso foi inválido', function () {
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
When('envio os dados sem a senha', function () { 
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

Then('retorna status 400 que é necessário ser informada', function () {
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
When('envio os dados com usuário inválido', function () { 
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

Then('retorna status 401 retorna sem acessar com usuário', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)

    expect(response.body)
      .to.have.property('detail')
      .and.to.eq('Usuário e/ou senha inválida')  
  })
})

// Não autenticar com senha inválida
When('envio os dados com senha inválida', function () { 
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

Then('retorna status 401 retorna sem acessar com senha', function () {
  cy.get('@response').then((response) => {
  
    expect(response.status).to.eq(401)

    expect(response.body)
      .to.have.property('detail')
      .and.to.eq('Usuário e/ou senha inválida')
  })
})