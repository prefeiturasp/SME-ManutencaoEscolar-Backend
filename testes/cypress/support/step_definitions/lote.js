import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Dado = Given
const Quando = When
const Então = Then

let token
let uuidLote

const lote = {
  "codigo_cadastro": "LOTE-TESTE",
  "nome": "Teste automatizado", 
  "status": true,
  "empresa": null,
  "periodo_inicial": "2026-01-01",
  "periodo_final": "2030-12-31",
  "diretorias_regionais": [
    7
  ]
}

Dado('que possuo um token de acesso a lote', function () {
  cy.gerar_token().then((token_valido) => {
    token = token_valido
  })
})

// Buscar empresa antes de cadastrar o lote
Quando('que busco a empresa para o lote', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/?nome=Teste%20manutenção`,
    headers: {
      accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
    timeout: 30000,
  }).then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body.results).to.be.an('array')
      .and.have.length.greaterThan(0)

    lote.empresa = response.body.results[0].uuid
  })
})

// Criar um novo lote
Quando('envio uma requisição POST no endpoint de lote', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: lote,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 201 criando um novo lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(201)   
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('codigo_cadastro')
    expect(response.body).to.have.property('empresa')
    expect(response.body).to.have.property('periodo_inicial')
    expect(response.body).to.have.property('periodo_final')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('diretorias_regionais')
    
    // Buscar o UUID do lote criado
    return cy.request({
      method: 'GET',
      url: `${Cypress.config('baseUrl')}/api/v1/lotes/?nome=Teste%20automatizado`,
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

      const loteCriado = responseGet.body.results[0]

      expect(loteCriado).to.have.property('uuid')

      uuidLote = loteCriado.uuid

      expect(uuidLote, 'UUID do lote criado')
        .to.be.a('string')
        .and.not.be.empty
    })
  })
})

// Não criar lote sem dados obrigatórios
Quando('envio uma requisição POST no endpoint de lote sem dados obrigatórios', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/`,
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

Então('retorna o status 400 sem criar lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400)   
  })
})

// Não criar lote sem autenticação
Quando('tento a requisição POST no endpoint de lote', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: lote,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem criar um novo lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Atualizar cadastro de lote
Quando('envio uma requisição PUT no endpoint de lote', function () {

  expect(uuidLote, 'UUID do lote')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PATCH',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${uuidLote}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: lote,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 atualizando um lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('codigo_cadastro')
    expect(response.body).to.have.property('empresa')
    expect(response.body).to.have.property('periodo_inicial')
    expect(response.body).to.have.property('periodo_final')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('diretorias_regionais')
  })
})

// Não atualizar lote sem dados obrigatórios
Quando('envio uma requisição PUT no endpoint de lote sem o id', function () {
  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/ /`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: lote,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 405 sem atualizar lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(405)
  })
})

// Não atualizar lote sem autenticação
Quando('tento a requisição PUT no endpoint de lote', function () {

  expect(uuidLote, 'UUID do lote')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${uuidLote}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: lote,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem atualizar lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Listar todos lotes
Quando('envio uma requisição GET no endpoint de lote', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/`,
    headers: {
      accept: 'application/json',      
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando todos lotes', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Listar somente lotes ativos
Quando('envio uma requisição GET no endpoint de lote status', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/?status=true`,
    headers: {
      accept: 'application/json',     
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando somente lotes ativos', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Buscar lote por nome
Quando('envio uma requisição GET no endpoint de lote nome', function () {

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/?nome=Teste%20automatizado`,
    headers: {
      accept: 'application/json', 
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando por nome do lote', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
    expect(response.body.results).to.have.length.greaterThan(0)

    const loteEncontrado = response.body.results[0]

    expect(loteEncontrado).to.have.property('uuid')

    uuidLote = loteEncontrado.uuid

    expect(uuidLote, 'UUID do lote')
      .to.be.a('string')
      .and.not.be.empty
  })
})

// Não buscar lote sem autenticação
Quando('tento a requisição GET no endpoint de lote', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/`,
    headers: {
      accept: 'application/json',  
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem buscar lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar detalhes do lote
Quando('envio uma requisição GET no endpoint de lote detalhes', function () {

  expect(uuidLote, 'UUID do lote')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${uuidLote}/`,
    headers: {
      accept: 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando detalhes do lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)    
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('codigo_cadastro')
    expect(response.body).to.have.property('empresa')
    expect(response.body).to.have.property('periodo_inicial')
    expect(response.body).to.have.property('periodo_final')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('diretorias_regionais')

    uuidLote = response.body.uuid
  })
})

// Não buscar detalhes de lotes inexistente
Quando('envio uma requisição GET no endpoint de lote detalhes inexistente', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${Cypress.env('UUID_LOTE_INVALIDO')}/`,
    headers: {
      accept: 'application/json',   
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 404 sen detalhes do lote', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não buscar detalhes de lote sem autenticação
Quando('tento a requisição GET no endpoint de lote detalhes', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${Cypress.env('UUID_LOTE')}/`,
    headers: {
      accept: 'application/json',
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem detalhes dos lotes', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Excluir cadastro de lote
Quando('envio uma requisição DELETE no endpoint de lote', function () {

  expect(uuidLote, 'UUID do lote')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${uuidLote}/`,
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

Então('retorna o status 204 excluindo o lote', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(204)
  })
})

// Não excluir cadastro de lote sem id
Quando('envio uma requisição DELETE no endpoint de lote sem o id', function () {
  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/ /`,
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

Então('retorna o status 404 sem excluir o lote', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não excluir lote sem autenticação
Quando('tento a requisição DELETE no endpoint de lote', function () {

  expect(uuidLote, 'UUID do lote')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/lotes/${uuidLote}/`,
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

Então('retorna o status 401 sem excluir lote', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(401)
  })
})