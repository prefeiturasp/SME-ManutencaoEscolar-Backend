import { Given } from '@badeball/cypress-cucumber-preprocessor'

const Dado = Given

Dado('eu acesso o sistema com a visualização {string}', function (visualizacao) {
	cy.configurar_visualizacao(visualizacao)
})

Dado('realizo login no sistema Manutenção Escolar com perfil {string}', function (perfil) {
cy.realizar_login(perfil)
})