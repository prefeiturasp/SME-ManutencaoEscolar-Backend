import Cargos_Localizadores from '../locators/cargos_locators'

const cargos_localizadores = new Cargos_Localizadores()

Cypress.Commands.add('acessar_cargos', () => { 
  cy.get(cargos_localizadores.menu_cadastro())
    .should('exist')
    .click()

  cy.get(cargos_localizadores.menu_cargos())
    .should('be.visible')
    .click()

  cy.url({ timeout: 10000 }).should('include', 'cargos')
})

Cypress.Commands.add('criar_cargo', () => {  
  cy.get(cargos_localizadores.btn_cadastrar_cargos())
    .should('be.visible')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/cargos/cadastrar')

  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.select_documento())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.opcoes_documento())
    .should('be.visible')
    .contains('Não')
    .click()

  cy.get(cargos_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cadastro_cargo', () => {
  cy.contains('O cargo foi cadastrado.')
})

Cypress.Commands.add('clicar_cadastrar_cargo', () => {  
  cy.get(cargos_localizadores.btn_cadastrar_cargos())
    .should('be.visible')
    .click() 
})

Cypress.Commands.add('validar_campos_preenchidos_cargo', () => {
  cy.get(cargos_localizadores.btn_salvar_cadastro())
    .should('not.exist')
})

Cypress.Commands.add('inserir_documento', () => {  
  cy.get(cargos_localizadores.btn_cadastrar_cargos())
    .should('be.visible')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/cargos/cadastrar')

  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.select_documento())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.opcoes_documento())
    .should('be.visible')
    .contains('Sim')
    .click()

  cy.get(cargos_localizadores.campo_nome_documento())
    .should('be.visible')
    .type('Teste automação')
})

Cypress.Commands.add('validar_campos_preenchidos_documento', () => {
  cy.contains('Informe ao menos um documento para este cargo.')
    .should('not.exist')
})

Cypress.Commands.add('clicar_cancelar_cadastro_cargo', () => {
  cy.get(cargos_localizadores.btn_cadastrar_cargos())
    .should('be.visible')
    .click() 
     
  cy.get(cargos_localizadores.btn_cancelar())
    .should('be.visible')
    .click() 
})

Cypress.Commands.add('validar_cancelar_cadastro_cargo', () => {
  cy.get(cargos_localizadores.btn_cadastrar_cargos())
    .should('be.visible')
})

Cypress.Commands.add('validar_cadastro_cargo_duplicado', () => {
  cy.contains('Cargo já cadastrado')
})

Cypress.Commands.add('cancelar_exclusao_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_excluir_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_cancelar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_editar_cargo', () => {
  cy.url({ timeout: 10000 }).should('include', '/editar')
})

Cypress.Commands.add('acionar_exclusao_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_excluir_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_cancelar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('nao_excluir_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Pintor')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo_permanente())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_excluir_cargo())
    .should('be.visible')
    .click()
  
  cy.get(cargos_localizadores.btn_confirmar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cargo_nao_excluido', () => {
  cy.contains('Não é possível excluir o cargo')  
})

Cypress.Commands.add('excluir_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_excluir_cargo())
    .should('be.visible')
    .click()
  
  cy.get(cargos_localizadores.btn_confirmar_exclusao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_exclusao_cargo', () => {
  cy.contains('O cargo foi excluído.')  
})

Cypress.Commands.add('editar_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()

  cy.url().should('include', '/cargos/').and('include', '/editar')

  cy.get(cargos_localizadores.select_documento())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.opcoes_documento())
    .contains('Não')
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_edicao_cargo', () => {
  cy.contains('As alterações foram salvas.')  
})

Cypress.Commands.add('cancelar_edicao_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()

  cy.url().should('include', '/cargos/').and('include', '/editar')

  cy.get(cargos_localizadores.btn_cancelar())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('editar_cargo_existente', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible') 
    .click()

  cy.url().should('include', '/cargos/').and('include', '/editar')

  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .clear()
	
	cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste cargo')

  cy.get(cargos_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('editar_campos_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()

  cy.url().should('include', '/cargos/').and('include', '/editar')

  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .clear()

  cy.get(cargos_localizadores.select_documento())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_campos_obrigatorios_cargo', () => {
  cy.contains('Campo obrigatório')  
})

Cypress.Commands.add('filtrar_nome_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_filtro_nome_cargo', () => {
  cy.get(cargos_localizadores.tbl_nome())
    .should('contain', 'Teste automação')  
})

Cypress.Commands.add('filtrar_documento_cargo', () => {
  cy.get(cargos_localizadores.select_documento())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.opcoes_documento())
    .should('be.visible')
    .contains('Não')
    .click()

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_filtro_documento_cargo', () => {
  cy.get(cargos_localizadores.tbl_documento())
    .should('contain', 'Não')  
})

Cypress.Commands.add('filtrar_cargo_inexistente', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Cargo inexistente')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_filtro_cargo_inexistente', () => {
  cy.contains('Não encontramos dados para esta busca')
})

Cypress.Commands.add('limpar_filtro_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Cargo inexistente')

  cy.get(cargos_localizadores.btn_limpar_filtro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_filtro_vazio_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .should('have.value', '')
})

Cypress.Commands.add('consultar_detalhes_cargo', () => {
  cy.get(cargos_localizadores.campo_nome())
    .should('be.visible')
    .type('Teste automação')

  cy.get(cargos_localizadores.btn_buscar_cargo())
    .should('be.visible')
    .click()

  cy.get(cargos_localizadores.btn_editar_cargo())
    .should('be.visible')
    .click()
})