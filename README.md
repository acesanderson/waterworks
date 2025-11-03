# Waterworks

A command-line AI assistant that understands your system's context to provide accurate, tailored sysadmin support.

Waterworks acts as a "helpful system administrator" by automatically injecting details about your operating system, hardware, and shell environment into its requests to a large language model. This allows it to generate commands and explanations that are specific to your machine, not generic boilerplate.

## Quick Start

### 1. Installation

Requires Python 3.8+.

```bash
pip install waterworks-cli
```

### 2. Configuration

The tool requires access to a large language model. Configure your API key as an environment variable. For example, for OpenAI models:

```bash
export OPENAI_API_KEY="sk-..."
```

### 3. First Use

Ask a question directly. The tool automatically provides system context to the model.

```bash
ask "How do I find the 5 largest files in my current directory?"
```

**Example Output (on a Linux system):**

```
To find the 5 largest files in the current directory on your system, you can use a combination of `du`, `sort`, and `head`. This command will work correctly in your zsh shell:

du -ah . | sort -rh | head -n 5
```

## Core Features

This example demonstrates how to pipe data to `ask` and use a local model for a more complex task.

1.  First, generate a list of running processes.
2.  Pipe the process list to `ask`.
3.  Instruct `ask` to identify the top 3 memory-consuming processes and suggest a command to terminate them, using a local model.

```bash
ps aux | ask --local "From this process list, identify the top 3 memory hogs. Provide a 'kill' command for the one with the highest PID."
```

This single command showcases:
*   **Piped Input**: `ask` seamlessly accepts input from other standard command-line tools.
*   **System Awareness**: It can parse OS-specific command outputs like `ps aux`.
*   **Local Model Support**: The `--local` flag directs the query to a local model instance (e.g., Ollama).
*   **Actionable Output**: Provides a direct, copy-pasteable command as requested.

## Installation and Setup

### Prerequisites

*   Python 3.8 or higher.
*   An API key for a remote LLM provider (e.g., OpenAI, Anthropic) or a running local LLM service (e.g., Ollama).

### Installation

The recommended installation method is via pip:

```bash
pip install waterworks-cli
```

### Environment Variables

For remote models, `ask` requires an API key. Set the appropriate environment variable for your provider.

```bash
# For OpenAI
export OPENAI_API_KEY="your-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

## Usage

### Basic Commands

The primary way to use the tool is by passing a query as a string.

```bash
ask "[YOUR QUESTION]"
```

It also accepts piped data from standard input, which is prepended to your query as context.

```bash
cat a_script.py | ask "What does this Python script do?"
```

### Command-Line Arguments

Key arguments for controlling `ask`'s behavior.

| Argument            | Alias | Description                                               | Default   |
| ------------------- | ----- | --------------------------------------------------------- | --------- |
| `--local`           | `-l`  | Use a local model instead of a remote API.                | `False`   |
| `--preferred-model` | `-p`  | Specify the model to use (e.g., `gpt-4o`, `claude-3-haiku`). | `flash`   |
| `--append`          | `-a`  | Append additional text or context to the query.           | `None`    |
| `--no-cache`        |       | Disable caching for the current query.                    | `False`   |
| `--verbose`         | `-v`  | Enable verbose output, showing progress and debug info.   | `False`   |
