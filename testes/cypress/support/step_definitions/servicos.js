import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Dado = Given
const Quando = When
const Então = Then

let token
let uuidServicos

const servico = {  
  nome: 'Teste automatizado',
  status: true 
}

Dado('que possuo um token de acesso a servicos', function () {
  cy.gerar_token().then((token_valido) => {
    token = token_valido
  })
})

// Criar um novo serviço
Quando('envio uma requisição POST no endpoint de servicos', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: servico,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 201 criando um novo serviço', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(201)   
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('status')
    
    // Buscar o UUID do serviço criado
    return cy.request({
      method: 'GET',
      url: `${Cypress.config('baseUrl')}/api/v1/servicos/?nome=Teste%20automatizado`,
      headers: {
        accept: 'application/json',    
        Authorization: `Bearer ${token}`
      },
      timeout: 30000,
      failOnStatusCode: false
    }).then((responseGet) => {

      expect(responseGet.status).to.eq(200)
      expect(responseGet.body).to.have.property('count')
      expect(responseGet.body).to.have.property('results')
      expect(responseGet.body.results).to.be.an('array')
      expect(responseGet.body.results).to.have.length.greaterThan(0)

      const servicoCriado = responseGet.body.results[0]

      expect(servicoCriado).to.have.property('uuid')

      uuidServicos = servicoCriado.uuid

      expect(uuidServicos, 'UUID do serviço criado')
        .to.be.a('string')
        .and.not.be.empty
    })
  })
})

// Não criar serviço sem dados obrigatórios
Quando('envio uma requisição POST no endpoint de servicos sem dados obrigatórios', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: {
      nome: ' ',
      status: true,      
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 400 sem criar serviço', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400)   
  })
})

// Não criar serviço sem autenticação
Quando('tento a requisição POST no endpoint de servicos', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: servico,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem criar um novo serviço', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Atualizar cadastro de serviço
Quando('envio uma requisição PUT no endpoint de servicos', function () {

  expect(uuidServicos, 'UUID do serviço')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PATCH',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${uuidServicos}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: servico,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 atualizando um serviço', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Não atualizar serviço sem dados obrigatórios
Quando('envio uma requisição PUT no endpoint de servicos sem o id', function () {
  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/ /`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: servico,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 405 sem atualizar serviço', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(405)
  })
})

// Não atualizar serviço sem autenticação
Quando('tento a requisição PUT no endpoint de servicos', function () {

  expect(uuidServicos, 'UUID do serviço')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${uuidServicos}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: servico,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem atualizar serviço', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Listar todos serviços
Quando('envio uma requisição GET no endpoint de servicos', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/`,
    headers: {
      accept: 'application/json',      
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando todos serviços', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Listar somente serviços ativos
Quando('envio uma requisição GET no endpoint de servicos status', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/?status=true`,
    headers: {
      accept: 'application/json',     
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando somente serviços ativos', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Buscar serviço por nome
Quando('envio uma requisição GET no endpoint de servicos nome', function () {

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/?nome=Teste%20automatizado`,
    headers: {
      accept: 'application/json', 
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando por nome do serviço', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
    expect(response.body.results).to.have.length.greaterThan(0)

    const servicoEncontrado = response.body.results[0]

    expect(servicoEncontrado).to.have.property('uuid')

    uuidServicos = servicoEncontrado.uuid

    expect(uuidServicos, 'UUID do serviço')
      .to.be.a('string')
      .and.not.be.empty
  })
})

// Não buscar serviço sem autenticação
Quando('tento a requisição GET no endpoint de servicos', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/`,
    headers: {
      accept: 'application/json',  
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem buscar serviços', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar detalhes do serviço
Quando('envio uma requisição GET no endpoint de servicos detalhes', function () {

  expect(uuidServicos, 'UUID do serviço')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${uuidServicos}/`,
    headers: {
      accept: 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando detalhes do serviços', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)    
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('status')    

    uuidServicos = response.body.uuid
  })
})

// Não buscar detalhes de serviço inexistente
Quando('envio uma requisição GET no endpoint de servicos detalhes inexistente', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${Cypress.env('UUID_SERVICO_INVALIDO')}/`,
    headers: {
      accept: 'application/json',   
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 404 sen detalhes do serviços', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não buscar detalhes de serviço sem autenticação
Quando('tento a requisição GET no endpoint de servico detalhes', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${Cypress.env('UUID_SERVICO')}/`,
    headers: {
      accept: 'application/json',
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem detalhes dos serviços', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Excluir cadastro de serviço
Quando('envio uma requisição DELETE no endpoint de servico', function () {

  expect(uuidServicos, 'UUID do serviço')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${uuidServicos}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response_delete')
})

Então('retorna o status 204 excluindo o serviço', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(204)
  })
})

// Não excluir cadastro de serviço sem id
Quando('envio uma requisição DELETE no endpoint de servico sem o id', function () {
  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/ /`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response_delete')
})

Então('retorna o status 404 sem excluir o serviço', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não excluir serviço sem autenticação
Quando('tento a requisição DELETE no endpoint de servico', function () {

  expect(uuidServicos, 'UUID do serviço')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/servicos/${uuidServicos}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response_delete')
})

Então('retorna o status 401 sem excluir serviço', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(401)
  })
})