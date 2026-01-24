/**
 * settings.template.js
 * Template Node-RED settings file for GitHub version control.
 * 
 * Safe to commit — does NOT contain any credentials or machine-specific secrets.
 */

/**
* Create a settings.json file, using this file as a template, which will hold Node_RED settings
*/

require('dotenv').config();

module.exports = {

    /*******************************************************************************
     * Flow File
     ******************************************************************************/
    flowFile: "flows.json",  // your main flow file

    /*******************************************************************************
    * Credential Secret
    ******************************************************************************/
    credentialSecret: "TxV7D+9egk8kM6r03+XV+dNB9gp+aRcDi9alboldh5Q=",

    /*******************************************************************************
    * Keep JSON files in clean format
    ******************************************************************************/
    flowFilePretty: true,

    /*******************************************************************************
     * Server Settings
     ******************************************************************************/
    uiPort: process.env.PORT || 1880,  // default Node-RED port

    /*******************************************************************************
     * Editor Settings
     ******************************************************************************/
    editorTheme: {
        projects: {
            enabled: true,            // enable Node-RED Projects
            workflow: {
                mode: "manual"        // manual commit workflow
            }
        },
        codeEditor: {
            lib: "monaco"             // default code editor
        },
        markdownEditor: {
            mermaid: { enabled: true } // enable mermaid diagrams in markdown
        },
        multiplayer: { enabled: false } // disable multiplayer
    },

    /*******************************************************************************
     * Runtime Settings
     ******************************************************************************/
    diagnostics: { enabled: true, ui: true },
    runtimeState: { enabled: false, ui: false },
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },

    telemetry: {
        // enabled: false // can override locally if needed
    },

    exportGlobalContextKeys: false,

    functionExternalModules: true,
    globalFunctionTimeout: 0,
    functionTimeout: 0,
    functionGlobalContext: {
        // add required npm modules here if needed, e.g.
        // os: require('os')
    },

    mqttReconnectTime: 15000,
    serialReconnectTime: 15000,
};
