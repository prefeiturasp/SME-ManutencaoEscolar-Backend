import Empresas_Localizadores from '../locators/empresas_locators'
import { faker } from '@faker-js/faker/locale/pt_BR'

const empresas_localizadores = new Empresas_Localizadores()

Cypress.Commands.add('acessar_empresas', () => { 
  cy.get(empresas_localizadores.menu_cadastro())
    .should('exist')
    .click()

  cy.get(empresas_localizadores.menu_empresas())
    .should('be.visible')
    .click()

  cy.url({ timeout: 10000 }).should('include', 'empresas')
})

Cypress.Commands.add('criar_empresa', () => {
  const cnpjEmpresa = faker.string.numeric(14)

  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/empresas/cadastrar')

  cy.get(empresas_localizadores.campo_nome())
    .should('be.visible')
    .type(Cypress.env('NOME_EMPRESA'))

  cy.get(empresas_localizadores.campo_cnpj())
    .should('be.visible')
    .type(cnpjEmpresa)

  cy.get(empresas_localizadores.campo_razao_social())
    .should('be.visible')
    .type(Cypress.env('RAZAO_SOCIAL'))

  cy.get(empresas_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.contains('Ativo')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.link_rastreio())
    .should('be.visible')
    .type(Cypress.env('LINK_RASTREIO'))

  cy.get(empresas_localizadores.campo_cep())
    .should('be.visible')
    .type(Cypress.env('CEP'))
    
  cy.get(empresas_localizadores.campo_logradouro())
    .should('be.visible')
    .type(Cypress.env('LOGRADOURO'))
    
  cy.get(empresas_localizadores.campo_numero())
    .should('be.visible')
    .type(Cypress.env('NUMERO'))
    
  cy.get(empresas_localizadores.campo_complemento())
    .should('be.visible')
    .type(Cypress.env('COMPLEMENTO'))  

  cy.get(empresas_localizadores.campo_cidade())
    .should('be.visible')
    .type(Cypress.env('CIDADE'))    

  cy.get(empresas_localizadores.campo_estado())
    .should('be.visible')
    .type(Cypress.env('ESTADO'))

  cy.contains('SP')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cadastro_empresa', () => {
  cy.contains('Responsável técnico')
})

Cypress.Commands.add('clicar_criar_empresa', () => {
  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/empresas/cadastrar') 

  cy.get(empresas_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.contains('Ativo')
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cadastro_nao_preenchido_empresa', () => {
  cy.contains('Próximo')
    .should('be.disabled')
})

Cypress.Commands.add('criar_empresa_inativa', () => {
  const cnpjEmpresa = faker.string.numeric(14)

  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/empresas/cadastrar')

  cy.get(empresas_localizadores.campo_nome())
    .should('be.visible')
    .type(Cypress.env('NOME_EMPRESA'))

  cy.get(empresas_localizadores.campo_cnpj())
    .should('be.visible')
    .type(cnpjEmpresa)

  cy.get(empresas_localizadores.campo_razao_social())
    .should('be.visible')
    .type(Cypress.env('RAZAO_SOCIAL'))

  cy.get(empresas_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.contains('Inativo')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.link_rastreio())
    .should('be.visible')
    .type(Cypress.env('LINK_RASTREIO'))

  cy.get(empresas_localizadores.campo_cep())
    .should('be.visible')
    .type(Cypress.env('CEP'))
    
  cy.get(empresas_localizadores.campo_logradouro())
    .should('be.visible')
    .type(Cypress.env('LOGRADOURO'))
    
  cy.get(empresas_localizadores.campo_numero())
    .should('be.visible')
    .type(Cypress.env('NUMERO'))
    
  cy.get(empresas_localizadores.campo_complemento())
    .should('be.visible')
    .type(Cypress.env('COMPLEMENTO'))  

  cy.get(empresas_localizadores.campo_cidade())
    .should('be.visible')
    .type(Cypress.env('CIDADE'))    

  cy.get(empresas_localizadores.campo_estado())
    .should('be.visible')
    .type(Cypress.env('ESTADO'))

  cy.contains('SP')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('campos_obrigatorios_criar_empresa', (campo) => {

  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/empresas/cadastrar')

  switch (campo) {

    case 'nome':
      cy.get(empresas_localizadores.campo_nome())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'cnpj':
      cy.get(empresas_localizadores.campo_cnpj())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'razao_social':
      cy.get(empresas_localizadores.campo_razao_social())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'status':
      cy.get(empresas_localizadores.campo_razao_social())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'cep':
      cy.get(empresas_localizadores.campo_cep())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'logradouro':
      cy.get(empresas_localizadores.campo_logradouro())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'numero':
      cy.get(empresas_localizadores.campo_numero())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'cidade':
      cy.get(empresas_localizadores.campo_cidade())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    case 'estado':
      cy.get(empresas_localizadores.campo_cidade())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()

      break

    default:
      throw new Error(`Campo não configurado: ${campo}`)
  }
})

Cypress.Commands.add('validar_campo_obrigatorio_empresa', () => {
  cy.contains(/é obrigatóri[ao]!/)
    .should('be.visible')
})

Cypress.Commands.add('clicar_detalhes_empresa', (campo) => {

  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

      cy.get(empresas_localizadores.campo_cidade())
        .should('be.visible')
        .click()

      cy.get(empresas_localizadores.link_rastreio())
        .should('be.visible')
        .click()
})

Cypress.Commands.add('abrir_cadastro_empresa', () => {
  cy.get(empresas_localizadores.btn_abrir_empresa())
    .should('be.visible')
    .first()
    .click()
})

Cypress.Commands.add('validar_consulta_empresa', () => {
  cy.contains('Empresas')  
})

Cypress.Commands.add('rastrear_empresa', () => {
  cy.get(empresas_localizadores.btn_rastrear_empresa())
    .should('be.visible')
    .first()
    .click()
})

Cypress.Commands.add('limpar_filtros_empresa', () => {
  cy.get(empresas_localizadores.btn_limpar_filtros())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('filtros_consulta_empresa', (campo) => {

  switch (campo) {

    case 'nome':
      cy.get(empresas_localizadores.campo_nome())
        .should('be.visible')
        .type(Cypress.env('NOME_EMPRESA'))

      cy.get(empresas_localizadores.btn_buscar())
        .should('be.visible')
        .click()

      break

    case 'cnpj':
      cy.get(empresas_localizadores.campo_cnpj())
        .should('be.visible')
        .type('1')

      cy.get(empresas_localizadores.btn_buscar())
        .should('be.visible')
        .click()

      break

    case 'razao_social':
      cy.get(empresas_localizadores.campo_razao_social())
        .should('be.visible')
        .type(Cypress.env('RAZAO_SOCIAL'))

      cy.get(empresas_localizadores.btn_buscar())
        .should('be.visible')
        .click()

      break

    case 'status':      
      cy.get(empresas_localizadores.select_status())
        .should('exist')
        .click()

      cy.contains('Ativo')
        .should('exist')
        .click()

      cy.get(empresas_localizadores.btn_buscar())
        .should('be.visible')
        .click()

      break

    default:
      throw new Error(`Campo não configurado: ${campo}`)
  }
})

Cypress.Commands.add('validar_filtros_empresa', () => {
  cy.contains('Empresas cadastradas')  
})

Cypress.Commands.add('filtros_sem_dados_empresa', (campo) => {

  switch (campo) {

    case 'cnpj':
      cy.get(empresas_localizadores.campo_cnpj())
        .should('be.visible')
        .type('00000000000000')

      cy.get(empresas_localizadores.btn_buscar())
        .should('be.visible')
        .click()

      break

    default:
      throw new Error(`Campo não configurado: ${campo}`)
  }
})

Cypress.Commands.add('validar_dados_nao_encontrados_empresa', () => {
  cy.contains('Não encontramos dados para esta busca')  
})

Cypress.Commands.add('criar_empresa_responsavel_tecnico', (tipoResponsavel) => {

  const cnpjEmpresa = faker.string.numeric(14)
  const nomeResponsavel = faker.person.fullName()
  const telefoneResponsavel = faker.phone.number('119########')
  const emailResponsavel = faker.internet.email()
  const numeroCrea = faker.string.numeric(10)
  const numeroArt = faker.string.numeric(12)

  cy.get(empresas_localizadores.btn_cadastrar_empresa())
    .contains('Cadastrar empresa')
    .click()

  cy.url({ timeout: 30000 })
    .should('include', '/empresas/cadastrar')

  cy.get(empresas_localizadores.campo_nome())
    .should('be.visible')
    .type(Cypress.env('NOME_EMPRESA'))

  cy.get(empresas_localizadores.campo_cnpj())
    .should('be.visible')
    .type(cnpjEmpresa)

  cy.get(empresas_localizadores.campo_razao_social())
    .should('be.visible')
    .type(Cypress.env('RAZAO_SOCIAL'))

  cy.get(empresas_localizadores.select_status())
    .should('be.visible')
    .click()

  cy.contains('Ativo')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.link_rastreio())
    .should('be.visible')
    .type(Cypress.env('LINK_RASTREIO'))

  cy.get(empresas_localizadores.campo_cep())
    .should('be.visible')
    .type(Cypress.env('CEP'))

  cy.get(empresas_localizadores.campo_logradouro())
    .should('be.visible')
    .type(Cypress.env('LOGRADOURO'))

  cy.get(empresas_localizadores.campo_numero())
    .should('be.visible')
    .type(Cypress.env('NUMERO'))

  cy.get(empresas_localizadores.campo_complemento())
    .should('be.visible')
    .type(Cypress.env('COMPLEMENTO'))

  cy.get(empresas_localizadores.campo_cidade())
    .should('be.visible')
    .type(Cypress.env('CIDADE'))

  cy.get(empresas_localizadores.campo_estado())
    .should('be.visible')
    .type(Cypress.env('ESTADO'))

  cy.contains('SP')
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.tipo_responsavel_tecnico(tipoResponsavel))
    .should('be.visible')
    .click()

  cy.contains(tipoResponsavel)
    .should('be.visible')
    .click()

  cy.get(empresas_localizadores.campo_nome_responsavel_tecnico())
    .should('be.visible')
    .type(nomeResponsavel)

  cy.get(empresas_localizadores.campo_telefone_responsavel_tecnico())
    .should('be.visible')
    .type(telefoneResponsavel)

  cy.get(empresas_localizadores.campo_email_responsavel_tecnico())
    .should('be.visible')
    .type(emailResponsavel)

  cy.get(empresas_localizadores.campo_numero_crea_responsavel_tecnico())
    .should('be.visible')
    .type(numeroCrea)

  cy.get(empresas_localizadores.campo_numero_art_responsavel_tecnico())
    .should('be.visible')
    .type(numeroArt)

  cy.get('input[type="file"]')
     .selectFile('cypress/fixtures/teste.pdf', { force: true })

  cy.get(empresas_localizadores.btn_salvar_cadastro())
    .should('be.visible')
    .click()  
})