import { Given, When, Then } from '@badeball/cypress-cucumber-preprocessor'
import { faker } from '@faker-js/faker'

const Dado = Given
const Quando = When
const Então = Then

let token
let uuidEmpresa

const cnpjEmpresa = faker.string.numeric(14)

const empresa = {
  nome: Cypress.env('NOME_EMPRESA'),
  cnpj: cnpjEmpresa,
  status: true,
  razao_social: Cypress.env('RAZAO_SOCIAL'),
  link_rastreio: Cypress.env('LINK_RASTREIO'),
  cep: Cypress.env('CEP'),
  logradouro: Cypress.env('LOGRADOURO'),
  numero: Cypress.env('NUMERO'),
  complemento: Cypress.env('COMPLEMENTO'),
  cidade: Cypress.env('CIDADE'),
  estado: Cypress.env('ESTADO'),
  responsaveis_tecnicos: [
    {
      tipo: 'preposto',
      nome: faker.person.fullName(),
      email: faker.internet.email(),
      telefone: faker.string.numeric(11)
    }
  ]
}

Dado('que possuo um token de acesso', function () {
  cy.gerar_token().then((token_valido) => {
    token = token_valido
  })
})

Dado('que não possuo um token de acesso', function () {
})

// Criar uma nova empresa
Quando('envio uma requisição POST no endpoint de empresas', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: empresa,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 201 cadastrando uma empresa', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(201)
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('cnpj')
    expect(response.body).to.have.property('razao_social')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('link_rastreio')
    expect(response.body).to.have.property('cep')
    expect(response.body).to.have.property('logradouro')
    expect(response.body).to.have.property('numero')
    expect(response.body).to.have.property('complemento')
    expect(response.body).to.have.property('cidade')
    expect(response.body).to.have.property('estado')

    expect(response.body.cnpj).to.eq(cnpjEmpresa)

    // Buscar o UUID da empresa criada
    return cy.request({
      method: 'GET',
      url: `${Cypress.config('baseUrl')}/api/v1/empresas/?cnpj=${cnpjEmpresa}`,
      headers: {
        accept: 'application/json',
        'Content-Type': 'application/json',
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

      const empresaCriada = responseGet.body.results[0]

      expect(empresaCriada).to.have.property('uuid')

      uuidEmpresa = empresaCriada.uuid

      expect(uuidEmpresa, 'UUID da empresa criada')
        .to.be.a('string')
        .and.not.be.empty
    })
  })
})

// Não criar empresa sem dados obrigatórios
Quando('envio uma requisição POST no endpoint de empresas sem dados obrigatórios', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: {
      nome: Cypress.env('NOME_EMPRESA'),
      cnpj: cnpjEmpresa,      
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 400 sem criar empresa', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400)   
  })
})

// Não criar uma nova empresa sem autenticação
Quando('tento a requisição POST no endpoint de empresas', function () {
  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: empresa,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem cadastrar empresas', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Atualizar uma empresa
Quando('envio uma requisição PUT no endpoint de empresas', function () {

  expect(uuidEmpresa, 'UUID da empresa')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${uuidEmpresa}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: empresa,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 atualizando uma empresa', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Não atualizar uma empresa sem id
Quando('envio uma requisição PUT no endpoint de empresas sem o id', function () {
  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/ /`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': Cypress.env('CSRF_TOKEN'),
      Authorization: `Bearer ${token}`
    },
    body: empresa,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 404 sem atualizar empresa', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não atualizar empresa sem autenticação
Quando('tento a requisição PUT no endpoint de empresas', function () {

  expect(uuidEmpresa, 'UUID da empresa')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'PUT',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${uuidEmpresa}/`,
    headers: {
      accept: '*/*',
      'Content-Type': 'application/json',
      'X-CSRFTOKEN': `token_invalido`,
      Authorization: `token_invalido`
    },
    body: empresa,
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem atualizar empresas', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Listar todas as empresas
Quando('envio uma requisição GET no endpoint de empresas', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando todas as empresas', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Listar somente empresas ativas
Quando('envio uma requisição GET no endpoint de empresas status', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/?status=true`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 listando somente empresas ativas', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Buscar por CNPJ da empresa
Quando('envio uma requisição GET no endpoint de empresas cnpj', function () {

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/?cnpj=${cnpjEmpresa}`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando por cnpj da empresa', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
    expect(response.body.results).to.have.length.greaterThan(0)

    const empresaEncontrada = response.body.results[0]

    expect(empresaEncontrada).to.have.property('uuid')

    uuidEmpresa = empresaEncontrada.uuid

    expect(uuidEmpresa, 'UUID da empresa')
      .to.be.a('string')
      .and.not.be.empty
  })
})

// Buscar por razão social da empresa
Quando('envio uma requisição GET no endpoint de empresas razão social', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/?razao_social=${encodeURIComponent(Cypress.env('RAZAO_SOCIAL'))}`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando por razão social da empresa', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Buscar por nome da empresa
Quando('envio uma requisição GET no endpoint de empresas nome', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/?nome=${encodeURIComponent(Cypress.env('NOME_EMPRESA'))}`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando por nome da empresa', function () {
  cy.get('@response').then((response) => {

    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('results')
    expect(response.body.results).to.be.an('array')
  })
})

// Não buscar empresas sem autenticação
Quando('tento a requisição GET no endpoint de empresas', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem buscar empresas', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar detalhes da empresa
Quando('envio uma requisição GET no endpoint de empresas detalhes', function () {

  expect(uuidEmpresa, 'UUID da empresa')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${uuidEmpresa}/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 200 buscando detalhes da empresa', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
    expect(response.body).to.have.property('id')
    expect(response.body).to.have.property('uuid')
    expect(response.body).to.have.property('nome')
    expect(response.body).to.have.property('cnpj')
    expect(response.body).to.have.property('status')
    expect(response.body).to.have.property('razao_social')
    expect(response.body).to.have.property('link_rastreio')
    expect(response.body).to.have.property('cep')
    expect(response.body).to.have.property('logradouro')
    expect(response.body).to.have.property('numero')
    expect(response.body).to.have.property('cidade')
    expect(response.body).to.have.property('estado')

    uuidEmpresa = response.body.uuid
  })
})

// Não buscar detalhes da empresa inexistente
Quando('envio uma requisição GET no endpoint de empresas detalhes inexistente', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${Cypress.env('UUID_EMPRESA_INVALIDO')}/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 404 sen detalhes da empresa', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não buscar detalhes empresas sem autenticação
Quando('tento a requisição GET no endpoint de empresas detalhes', function () {
  return cy.request({
    method: 'GET',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${Cypress.env('UUID_EMPRESA')}/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: 'token_invalido'
    },
    timeout: 30000,
    failOnStatusCode: false
  }).as('response')
})

Então('retorna o status 401 sem detalhes das empresas', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Excluir cadastro de uma empresa
Quando('envio uma requisição DELETE no endpoint de empresas', function () {

  expect(uuidEmpresa, 'UUID da empresa')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${uuidEmpresa}/`,
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

Então('retorna o status 204 excluindo a empresa', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(204)
  })
})

// Não excluir cadastro de uma empresa sem id
Quando('envio uma requisição DELETE no endpoint de empresas sem o id', function () {
  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/ /`,
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

Então('retorna o status 404 sem excluir a empresa', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não excluir empresas sem autenticação
Quando('tento a requisição DELETE no endpoint de empresas', function () {

  expect(uuidEmpresa, 'UUID da empresa')
    .to.exist
    .and.to.be.a('string')
    .and.not.be.empty

  return cy.request({
    method: 'DELETE',
    url: `${Cypress.config('baseUrl')}/api/v1/empresas/${uuidEmpresa}/`,
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

Então('retorna o status 401 sem excluir empresas', function () {
  cy.get('@response_delete').then((response) => {
    expect(response.status).to.eq(401)
  })
})