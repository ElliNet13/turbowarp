class MicrobitWebUSB {
  constructor(runtime) {
    this.runtime = runtime;
    this.device = null;
    this.interfaceNumber = null;
    this.endpointIn = null;
    this.endpointOut = null;
    this.lastReceived = '';
    this._triggerFlag = false;
    this._buffer = '';
    this._delimiter = '\r\n'; // default delimiter
    this._startFlagResetLoop();
  }

  getInfo() {
    return {
      id: 'microbitWebUSB',
      name: 'micro:bit WebUSB',
      blocks: [
        {
          opcode: 'connect',
          blockType: Scratch.BlockType.COMMAND,
          text: 'connect to micro:bit with delimiter [DELIM]',
          arguments: {
            DELIM: {
              type: Scratch.ArgumentType.STRING,
              defaultValue: '\\n',
            }
          }
        },
        {
          opcode: 'sendText',
          blockType: Scratch.BlockType.COMMAND,
          text: 'send [TEXT] to micro:bit',
          arguments: {
            TEXT: {
              type: Scratch.ArgumentType.STRING,
              defaultValue: 'hello',
            }
          }
        },
        {
          opcode: 'lastReceivedText',
          blockType: Scratch.BlockType.REPORTER,
          text: 'last received text',
        },
        {
          opcode: 'whenReceived',
          blockType: Scratch.BlockType.HAT,
          text: 'when micro:bit receives data',
        }
      ]
    };
  }

  async connect(args) {
    this._delimiter = this._unescapeDelimiter(args.DELIM);
    try {
      this.device = await navigator.usb.requestDevice({
        filters: [{ vendorId: 0x0D28 }]
      });
      await this.device.open();
      if (this.device.configuration === null) {
        await this.device.selectConfiguration(1);
      }

      // Find interface with bulk endpoints
      for (const iface of this.device.configuration.interfaces) {
        for (const alt of iface.alternates) {
          if (alt.endpoints.some(e => e.direction === 'out')) {
            this.interfaceNumber = iface.interfaceNumber;
            for (const ep of alt.endpoints) {
              if (ep.direction === 'in') this.endpointIn = ep.endpointNumber;
              if (ep.direction === 'out') this.endpointOut = ep.endpointNumber;
            }
            break;
          }
        }
      }

      await this.device.claimInterface(this.interfaceNumber);
      this._readLoop();
      console.log('Connected to micro:bit WebUSB');
    } catch (e) {
      console.error('Connection failed:', e);
    }
  }

  _unescapeDelimiter(input) {
    return input
      .replace(/\\r/g, '\r')
      .replace(/\\n/g, '\n')
      .replace(/\\t/g, '\t');
  }

  async sendText(args) {
    if (!this.device || !this.endpointOut) return;
    const encoder = new TextEncoder();
    await this.device.transferOut(this.endpointOut, encoder.encode(args.TEXT + '\n'));
  }

  lastReceivedText() {
    return this.lastReceived;
  }

  whenReceived() {
    if (this._triggerFlag) {
      this._triggerFlag = false;
      return true;
    }
    return false;
  }

  async _readLoop() {
    const decoder = new TextDecoder();
    while (this.device) {
      try {
        const result = await this.device.transferIn(this.endpointIn, 64);
        const chunk = decoder.decode(result.data);
        this._buffer += chunk;

        let index;
        while ((index = this._buffer.indexOf(this._delimiter)) !== -1) {
          const message = this._buffer.substring(0, index).trim();
          this._buffer = this._buffer.substring(index + this._delimiter.length);
          if (message.length > 0) {
            this.lastReceived = message;
            this._triggerFlag = true;
          }
        }
      } catch (e) {
        console.error('Read error:', e);
        break;
      }
    }
  }

  _startFlagResetLoop() {
    setInterval(() => {
      this._triggerFlag = false;
    }, 100);
  }
}

Scratch.extensions.register(new MicrobitWebUSB());
