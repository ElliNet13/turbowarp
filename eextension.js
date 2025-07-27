(function(Scratch) {
    'use strict';
    // @ts-ignore
    const vm = Scratch.vm;
    
    // Define the SandboxError class outside of the Extension class
    class SandboxError extends Error {
        constructor() {
            super("Block sandboxed"); // Call the super constructor with the error message
            this.name = this.constructor.name; // Set the name of the error to the class name
        }
    }

    class Extension {
        // @ts-ignore
        getInfo() {
            return {
                id: "eextension",
                name: "ElliNet13's Extension",
                color1: '#009CCC',
                blocks: [
                    {
                        opcode: "__NOUSEOPCODE",
                        blockType: Scratch.BlockType.LABEL,
                        text: "You do not need to run these blocks without sandbox",
                    },
                    {
                        opcode: 'reverseText',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'Reverse text [TEXT]',
                        arguments: {
                            TEXT: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: 'Hello, world!'
                            }
                        }
                    },
                    {
                        opcode: 'sandboxed',
                        blockType: Scratch.BlockType.BOOLEAN,
                        text: 'Is extension sandboxed?',
                        arguments: {}
                    },
                    {
                        opcode: "__NOUSEOPCODE",
                        blockType: Scratch.BlockType.LABEL,
                        text: "These blocks need to run without sandbox",
                    },
                    {
                        opcode: 'openSite',
                        blockType: Scratch.BlockType.COMMAND,
                        text: 'Open site [URL]',
                        arguments: {
                            URL: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: 'https://ellinet13.github.io/'
                            }
                        }
                    },
                    {
                        opcode: 'alerter',
                        blockType: Scratch.BlockType.COMMAND,
                        text: 'Alert with message [MESSAGE]',
                        arguments: {
                            MESSAGE: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: 'Hello, world!'
                            }
                        }
                    }
                ]
            };
        }

        reverseText(args) {
            return args.TEXT.split('').reverse().join('');
        }
        sandboxed() {
            try {
            if (window.parent !== window) {
                // The code is running in an iframe
                if (window.parent.origin !== window.origin) {
                    return true;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        } catch {
            return true
        }
        }
        openSite(args) {
                window.open(args.URL, '_blank'); // Opens the specified URL in a new tab
        }
        alerter(args) {
            alert(args.MESSAGE)
        }
    }
    Scratch.extensions.register(new Extension());
    // @ts-ignore
})(Scratch);
