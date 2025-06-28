# AI Workbench

A powerful AI-powered workbench with advanced reasoning, learning, and system monitoring capabilities.

## Features

- 🧠 AI Brain with multiple specialized engines (reasoning, coding, analysis, optimization)
- 🔌 REST API and WebSocket interfaces
- 📊 System monitoring and metrics
- 🛡️ Built-in error handling and recovery
- 📦 Modular and extensible architecture

## Prerequisites

- Node.js 16+ (LTS recommended)
- npm or yarn
- API keys for AI services (OpenAI, Anthropic, etc.)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-workbench.git
   cd ai-workbench
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the configuration values in `.env`

## Usage

### Starting the Server

```bash
# Development mode with hot-reload
npm run dev

# Production mode
npm start
```

### API Endpoints

- `GET /health` - Health check
- `POST /api/think` - Process a prompt with the AI Brain
- `GET /api/system/state` - Get current system state

### WebSocket

The server also provides a WebSocket interface at `ws://localhost:3000` with the following events:

- `think` - Send a prompt to the AI Brain
  ```javascript
  socket.emit('think', { prompt: 'Hello, world!' }, (response) => {
    console.log('Response:', response);
  });
  ```

## Development

### Project Structure

```
ai-workbench/
├── api/                  # API server implementation
├── core/                 # Core modules (AI Brain, error handling, etc.)
├── examples/             # Example scripts
├── monitors/             # System monitoring components
├── tests/                # Test files
├── .env                 # Environment variables
├── package.json         # Project configuration
└── README.md            # This file
```

### Scripts

- `npm start` - Start the server in production mode
- `npm run dev` - Start the server in development mode with hot-reload
- `npm test` - Run tests
- `npm run lint` - Lint the code
- `npm run format` - Format the code

## Configuration

See `.env.example` for all available configuration options.

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
