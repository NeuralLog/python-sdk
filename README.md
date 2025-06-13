# NeuralLog Python SDK

The Python SDK for NeuralLog provides a client library for interacting with the NeuralLog server from Python applications. It offers a simple, intuitive API for logging messages at different levels.

## Requirements

- Python 3.8 or later
- requests library

## Installation

```bash
pip install neurallog-sdk
```

## Basic Usage

```python
from neurallog_sdk import NeuralLog, NeuralLogConfig

# Configure the SDK
config = NeuralLogConfig(
    server_url="http://localhost:3030",
    namespace="default",
    async_enabled=True,
    batch_size=100,
    batch_interval_ms=5000
)
NeuralLog.configure(config)

# Get a logger
logger = NeuralLog.get_logger("my-application")

# Log a simple message
logger.info("Hello, world!")

# Log with structured data
data = {
    "user": "john.doe",
    "action": "login",
    "ip": "192.168.1.1"
}
logger.info("User logged in", data=data)

# Log an error with exception
try:
    # Some code that might throw an exception
    raise Exception("Something went wrong")
except Exception as e:
    logger.error("Failed to process request", exception=e)
```

## Configuration Options

The Python SDK supports various configuration options:

```python
config = NeuralLogConfig(
    # Required settings
    server_url="https://logs.example.com",
    namespace="production",

    # Optional settings
    api_key="your-api-key",
    batch_size=100,
    batch_interval_ms=5000,
    max_retries=3,
    retry_backoff_ms=1000,
    async_enabled=True,
    debug_enabled=False,

    # HTTP client settings
    timeout_ms=30000,
    max_connections=10,

    # Custom HTTP headers
    headers={
        "X-Custom-Header": "value"
    }
)

NeuralLog.configure(config)
```

## Advanced Features

### Context Data

```python
# Set global context data for all loggers
NeuralLog.set_global_context({
    "application": "my-application",
    "environment": "production",
    "version": "1.0.0"
})

# Set logger-specific context data
logger.set_context({
    "service": "user-service",
    "instance": "user-service-1"
})
```

### Batching

The SDK supports batching of log messages to improve performance:

```python
config = NeuralLogConfig(
    server_url="http://localhost:3030",
    namespace="default",
    async_enabled=True,
    batch_size=100,
    batch_interval_ms=5000
)
NeuralLog.configure(config)
```

With batching enabled, log messages are queued and sent in batches when:
- The batch size is reached
- The batch interval elapses
- The `flush` method is called

### Flushing

To ensure all pending log messages are sent, you can flush the logger:

```python
# Flush a specific logger
logger.flush()

# Flush all loggers
NeuralLog.flush_all()
```

## Framework Integration

The NeuralLog Python SDK can be integrated with popular Python logging frameworks. Framework-specific adapters will be added in future releases.

## Building from Source

```bash
# Clone the repository
git clone https://github.com/NeuralLog/python-sdk.git
cd python-sdk

# Install in development mode
pip install -e .

# Run the tests
python -m unittest discover tests
```

## Documentation

Detailed documentation is available in the [docs](./docs) directory:

- [API Reference](./docs/api.md)
- [Configuration](./docs/configuration.md)
- [Architecture](./docs/architecture.md)
- [Examples](./docs/examples)

For integration guides and tutorials, visit the [NeuralLog Documentation Site](https://neurallog.github.io/docs/).

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Related NeuralLog Components

- [NeuralLog Auth](https://github.com/NeuralLog/auth) - Authentication and authorization
- [NeuralLog Server](https://github.com/NeuralLog/server) - Core server functionality
- [NeuralLog Web](https://github.com/NeuralLog/web) - Web interface components
- [NeuralLog TypeScript Client SDK](https://github.com/NeuralLog/typescript-client-sdk) - TypeScript client SDK
- [NeuralLog Java Client SDK](https://github.com/NeuralLog/Java-client-sdk) - Java client SDK

## License

MIT
