import Login_ME_Localizadores from '../locators/login_locators'

const login_ME_Localizadores = new Login_ME_Localizadores

Cypress.Commands.add('configurar_visualizacao', (device) => {
	cy.visit(Cypress.config('baseUrl'))
	switch (device) {
		case 'web':
			cy.viewport(1920, 1080)
			break
		default:
			break
	}
})

Cypress.Commands.add('login_ME', (device) => {
	cy.configurar_visualizacao(device)
})

Cypress.Commands.add('realizar_login', (perfil) => {
	switch (perfil) {
		case "Diretor":
			cy.get(login_ME_Localizadores.campo_usuario())
			  .type(Cypress.env('LOGIN_DIRETOR'))
			cy.get(login_ME_Localizadores.campo_senha())
			  .type(Cypress.env('SENHA'))
			cy.get(login_ME_Localizadores.botao_acessar())
			  .should('be.visible').click()

			cy.url().should('include', 'manutencao-escolar')
			break

		default:
			console.error("Perfil não encontrado!")
	}
})

Cypress.Commands.add('clicar_botao_acessar', () => {
	cy.get(login_ME_Localizadores.botao_acessar())
	  .should('be.visible')
})

Cypress.Commands.add('validar_acesso_me', () => {
	cy.contains('Sair')
	  .should('be.visible')
})

Cypress.Commands.add('validar_campos_obrigatorios_acesso', (campo) => {

  if (campo === 'login') {    
    cy.get(login_ME_Localizadores.campo_senha())
      .type(Cypress.env('SENHA'))
  
  cy.get(login_ME_Localizadores.botao_acessar())
	  .should('be.visible')
  }

  if (campo === 'senha') {    
    cy.get(login_ME_Localizadores.campo_usuario())
      .type(Cypress.env('LOGIN_DIRETOR'))

  cy.get(login_ME_Localizadores.botao_acessar())
	  .should('be.visible')
  }

  if (campo === 'ambos') {    
  cy.get(login_ME_Localizadores.botao_acessar())
	  .should('be.disabled')
  }  
})

Cypress.Commands.add('validar_caracteres_acesso', (campo, dado) => {

  if (campo === 'login') {
    cy.get(login_ME_Localizadores.campo_usuario())
      .clear()
      .type(dado)

    cy.get(login_ME_Localizadores.campo_senha())
      .clear()
      .type(Cypress.env('SENHA'))
  }

  if (campo === 'senha') {
    cy.get(login_ME_Localizadores.campo_usuario())
      .clear()
      .type(Cypress.env('LOGIN_DIRETOR'))

    cy.get(login_ME_Localizadores.campo_senha())
      .clear()
      .type(dado)
  }

  cy.get(login_ME_Localizadores.botao_acessar())
    .should('be.visible')
    .click()

  cy.get(login_ME_Localizadores.texto_obrigatorio())
    .should('be.visible')

  if (campo === 'login') {
    cy.contains('Certifique-se de que este campo tenha mais de 7 caracteres.')
      .should('be.visible')
  }

  if (campo === 'senha') {
    cy.contains('Usuário e/ou senha inválida')
      .should('be.visible')
  }
})

Cypress.Commands.add('validar_acesso_invalido', (campo, dado) => {

  if (campo === 'login') {
    cy.get(login_ME_Localizadores.campo_usuario())
      .clear()
      .type(dado)

    cy.get(login_ME_Localizadores.campo_senha())
      .clear()
      .type(Cypress.env('SENHA'))
  }

  if (campo === 'senha') {
    cy.get(login_ME_Localizadores.campo_usuario())
      .clear()
      .type(Cypress.env('LOGIN_DIRETOR'))

    cy.get(login_ME_Localizadores.campo_senha())
      .clear()
      .type(dado)
  }

  cy.get(login_ME_Localizadores.botao_acessar())
    .should('be.visible')
    .click()

  cy.get(login_ME_Localizadores.texto_obrigatorio())
    .should('be.visible')

  if (campo === 'login') {
    cy.contains('Certifique-se de que este campo tenha mais de 7 caracteres.')
      .should('be.visible')
  }

  if (campo === 'senha') {
    cy.contains('Usuário e/ou senha inválida')
      .should('be.visible')
  }
})