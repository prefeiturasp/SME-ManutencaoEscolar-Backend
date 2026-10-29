import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'

const Dado = Given
const Quando = When
const Então = Then

let token
let uuidCargo

const cargo = {
  "nome": "Teste automatizado",
  "exige_documento": true,
  "status": true,
  "documentos": [
    {
      "nome": "Certificado teste"
    },
    {
      "nome": "Comprovante de teste"
    }
  ]
}

Dado('que possuo um token de acesso a cargo', function () {
  cy.gerar_token().then((token_valido) => {
    token = token_valido
  })
})

// Criar um novo cargo
Quando('envio uma requisição POST no endpoint de cargo', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: cargo,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 201 criando um novo cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(201)   
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('exige_documento')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('documentos')
    
    // Buscar o UUID do cargo criado
    return cy.request({
      method: 'GET',
      url: `${Cypress.config('baseUrl')}/api/v1/cargos/?nome=Teste%20automatizado`,
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

      const cargoCriado = responseGet.body.results[0]

      expect(cargoCriado).to.have.property('uuid')

      uuidCargo = cargoCriado.uuid

      expect(uuidCargo, 'UUID do cargo criado')
        .to.be.a('string')
        .and.not.be.empty
    })
  })
})

// Não criar cargo sem dados obrigatórios
Quando('envio uma requisição POST no endpoint de cargo sem dados obrigatórios', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/`,
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

Então('retorna o status 400 sem criar cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400)   
  })
})

// Não criar cargo sem autenticação
Quando('tento a requisição POST no endpoint de cargo', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: cargo,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem criar um novo cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Atualizar cadastro de cargo
Quando('envio uma requisição PUT no endpoint de cargo', function () {

  expect(uuidCargo, 'UUID do cargo')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PATCH',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${uuidCargo}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: cargo,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 atualizando um cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('exige_documento')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('documentos')
  })
})

// Não atualizar cargo sem dados obrigatórios
Quando('envio uma requisição PUT no endpoint de cargo sem o id', function () {
  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/ /`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: cargo,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 405 sem atualizar cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(405)
  })
})

// Não atualizar cargo sem autenticação
Quando('tento a requisição PUT no endpoint de cargo', function () {

  expect(uuidCargo, 'UUID do cargo')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${uuidCargo}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: cargo,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem atualizar cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Listar todos cargos
Quando('envio uma requisição GET no endpoint de cargo', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/`,
    headers: {
      accept: 'application/json',      
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando todos cargos', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Listar somente cargos ativos
Quando('envio uma requisição GET no endpoint de cargo status', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/?status=true`,
    headers: {
      accept: 'application/json',     
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando somente cargos ativos', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Buscar cargo por nome
Quando('envio uma requisição GET no endpoint de cargo nome', function () {

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/?nome=Teste%20automatizado`,
    headers: {
      accept: 'application/json', 
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando por nome do cargo', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
    expect(response.body.results).to.have.length.greaterThan(0)

    const cargoEncontrado = response.body.results[0]

    expect(cargoEncontrado).to.have.property('uuid')

    uuidCargo = cargoEncontrado.uuid

    expect(uuidCargo, 'UUID do cargo')
      .to.be.a('string')
      .and.not.be.empty
  })
})

// Não buscar cargo sem autenticação
Quando('tento a requisição GET no endpoint de cargo', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/`,
    headers: {
      accept: 'application/json',  
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem buscar cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar detalhes do cargo
Quando('envio uma requisição GET no endpoint de cargo detalhes', function () {

  expect(uuidCargo, 'UUID do cargo')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${uuidCargo}/`,
    headers: {
      accept: 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando detalhes do cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('id')
    expect(response.body).to.have.property('uuid')    
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('exige_documento')
    expect(response.body).to.have.property('documentos')   

    uuidCargo = response.body.uuid
  })
})

// Não buscar detalhes de cargos inexistente
Quando('envio uma requisição GET no endpoint de cargo detalhes inexistente', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${Cypress.env('UUID_CARGO_INVALIDO')}/`,
    headers: {
      accept: 'application/json',   
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 404 sen detalhes do cargo', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não buscar detalhes de cargo sem autenticação
Quando('tento a requisição GET no endpoint de cargo detalhes', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${Cypress.env('UUID_CARGO')}/`,
    headers: {
      accept: 'application/json',
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem detalhes dos cargos', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Excluir cadastro de cargo
Quando('envio uma requisição DELETE no endpoint de cargo', function () {

  expect(uuidCargo, 'UUID do cargo')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${uuidCargo}/`,
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

Então('retorna o status 204 excluindo o cargo', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(204)
  })
})

// Não excluir cadastro de cargo sem id
Quando('envio uma requisição DELETE no endpoint de cargo sem o id', function () {
  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/ /`,
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

Então('retorna o status 404 sem excluir o cargo', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não excluir cargo sem autenticação
Quando('tento a requisição DELETE no endpoint de cargo', function () {

  expect(uuidCargo, 'UUID do cargo')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/cargos/${uuidCargo}/`,
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

Então('retorna o status 401 sem excluir cargo', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(401)
  })
})