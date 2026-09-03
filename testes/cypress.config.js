import { defineConfig } from 'cypress'
import allureWriter from '@shelex/cypress-allure-plugin/writer.js'
import { cloudPlugin } from 'cypress-cloud/plugin'
import dotenv from 'dotenv'

import createBundler from '@bahmutov/cypress-esbuild-preprocessor'
import { addCucumberPreprocessorPlugin } from '@badeball/cypress-cucumber-preprocessor'
import { createEsbuildPlugin } from '@badeball/cypress-cucumber-preprocessor/esbuild'

dotenv.config()

export default defineConfig({
  e2e: {
    watchForFileChanges: true,
    baseUrl: 'https://qa-manutencao-escolar.sme.prefeitura.sp.gov.br',
    supportFile: 'cypress/support/e2e.js',

    viewportWidth: 1920,
    viewportHeight: 1080,
    video: false,
    env: {
      TAGS: 'not @ignore',
    },

    retries: {
      runMode: 2,
      openMode: 0,
    },
    screenshotOnRunFailure: false,
    chromeWebSecurity: false,
    experimentalRunAllSpecs: true,
    failOnStatusCode: false,

    specPattern: 'cypress/e2e/**/*.feature',

    defaultCommandTimeout: 60000,
    requestTimeout: 60000,
    execTimeout: 60000,
    pageLoadTimeout: 60000,
    waitForAnimations: true,
    animationDistanceThreshold: 5,

    async setupNodeEvents(on, config) {
      await addCucumberPreprocessorPlugin(on, config)

      on(
        'file:preprocessor',
        createBundler({
          plugins: [createEsbuildPlugin(config)],
        })
      )

      // =====================
      // Allure
      // =====================
      allureWriter(on, config)

      // =====================
      // Cypress Cloud
      // =====================
      const enhancedConfig = await cloudPlugin(on, config)

      // =====================
      // ENV
      // =====================
      const envKeys = [
        'LOGIN_DIRETOR',
        'LOGIN_INVALIDO',
        'SENHA',
        'SENHA_INVALIDA',
        'CNPJ',
        'RAZAO_SOCIAL',
        'NOME_EMPRESA',
        'UUID_EMPRESA',
        'LINK_RASTREIO',
        'CEP',
        'LOGRADOURO',
        'NUMERO',
        'COMPLEMENTO',
        'CIDADE',
        'ESTADO',
      ]

      const customVariable = Object.fromEntries(
        envKeys.map((key) => [key, process.env[key] ?? ''])
      )

      enhancedConfig.env = { ...enhancedConfig.env, ...customVariable }

      return enhancedConfig
    },
  },
})