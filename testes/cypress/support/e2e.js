// Plugin do Allure (deve vir primeiro)
require('@shelex/cypress-allure-plugin')

// Comandos personalizados - API

// Comandos personalizados - UI
require('./commands_ui/commands_login')

// Evita falhas silenciosas caso algum comando seja removido ou renomeado
Cypress.on('uncaught:exception', (err, runnable) => {
  return false
})



