Cypress.Commands.add('autenticar_login', (usuario, senha) => {
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrl') + '/api/v1/login/',
    body: { login: usuario, senha: senha },
    timeout: 60000,
    failOnStatusCode: false,
  }).then((response) => {
    if (response.status === 200) {
      globalThis.token = response.body.token
    }
    return response
  })
})

Cypress.Commands.add('gerar_token', () => {
  const tokenExistente = Cypress.env('TOKEN')

  if (tokenExistente) {
    return cy.wrap(tokenExistente, { log: false })
  }

  return cy.request({
    method: 'POST',
    url: `${Cypress.config('baseUrl')}/api/v1/login/`,
    body: {
      login: Cypress.env('LOGIN_DIRETOR'),
      senha: Cypress.env('SENHA'),
    },
    headers: {
      'Content-Type': 'application/json'
    },
    timeout: 60000,
    failOnStatusCode: false,
    log: false
  }).then((response) => {

    expect(response.status).to.eq(200)

    const token = response.body.access

    if (!token) {
       throw new Error('Token não gerado')
   }

    Cypress.env('TOKEN', token)

    return token
  })
})