# Python Repository Template
- Originally created by Giovanni Cometti (link below)
- Developer docs journal format from lmmx's giacometti repo: (https://github.com/lmmx/giacometti).
- towncrier and direnv recipe added by: optimal prime

The ultimate 2025 Python repository template. Simple, fast, customizable, and ready to use.

This template is an opinionated take on an optimal python stack in 2025 and beyond.  

It stemmed from realizing that when vibe-coding, the CHANGELOG.md is oftentimes more useful than when you make
the AI write documentation that ends up being too hard to find when you need it and confusing AI agents.

That was when it was clear that lmmx's approach to journaling was way better, and more along the lines
of what I'd been doing anyway.

Once I did a bit more research on how to properly use CHANGELOG.md, I found towncrier and added it in.

The goal is to still keep a quite minimal python package so as to not needlessly bog down your project with
too many dependencies, which will bloat your future docker images.  

Speaking of which, that part has not been tested and neither have the github pre-commit hooks. 

This template is a work in progress and hopefully will evolve over time for various use cases. 

In fact, the next one will be a branch that's for vibe-coding with AI and after that, probably one that's
specifically for deploying on Railway, Netlify, or Vercel.

Enjoy!

---
Giovannia Cometti wrote a blog post about this template! Check it out [here](https://giovannigiacometti.github.io/posts/python-template/)

## 🎯 Core Features

### Development Tools

- 📦 UV - Ultra-fast Python package manager
- 🚀 Just - Modern command runner with powerful features
- 💅 Ruff - Lightning-fast linter and formatter
- 🔍 Mypy - Static type checker
- 🧪 Pytest - Testing framework with fixtures and plugins
- 🧾 Loguru - Python logging made simple

### Infrastructure

- 🛫 Pre-commit hooks
- 🐳 Docker support with multi-stage builds and distroless images
- 🔄 GitHub Actions CI/CD pipeline


## Usage

The template is based on [UV](https://docs.astral.sh/) as package manager and [Just](https://github.com/casey/just) as command runner. You need to have both installed in your system to use this template.

### Quick Start

1. **Initialize your project** (run this first in a fresh clone):
   ```bash
   just init
   ```
   
   This will guide you through setting up your project with:
   - Custom project name and metadata
   - Choice of project structure (default, package, or library)
   - Python version configuration
   - Towncrier setup for changelog management

2. **Set up your environment** (optional but recommended):
   ```bash
   cp .envrc.example .envrc
   direnv allow
   ```

3. **Install dependencies**:
   ```bash
   just dev-sync
   ```

4. **Install pre-commit hooks**:
   ```bash
   just install-hooks
   ```

### Project Structures

The `just init` command offers three project structures:

- **default**: Simple script-based project with a basic package
- **package**: Package-based project with `src/` layout
- **library**: Library-style project with full structure including `src/`, `tests/`, and organized modules

### Manual Setup

If you prefer to skip the automated initialization, you can manually run:

```bash
just dev-sync
```

to create a virtual environment and install all the dependencies, including the development ones. If instead you want to build a "production-like" environment, you can run

```bash
just prod-sync
```

In both cases, all extra dependencies will be installed (notice that the current pyproject.toml file has no extra dependencies).

### Formatting, Linting and Testing

You can configure Ruff by editing the `.ruff.toml` file. It is currently set to the default configuration.

Format your code:

```bash
just format
```

Run linters (ruff and mypy):

```bash
just lint
```

Run tests:

```bash
just test
```

Do all of the above:

```bash
just validate
```

### Executing

The code is a simple hello world example, which just requires a number as input. It will output the sum of the provided number with a random number.
You can run the code with:

```bash
just run 5
```

### Docker

The template includes a multi stage Dockerfile, which produces an image with the code and the dependencies installed. You can build the image with:

```bash
just dockerize
```

### Changelog Management

This template includes [Towncrier](https://towncrier.readthedocs.io/) for automated changelog management:

1. **Add news fragments**: Create files in `newsfragments/` with format `<type>.<ticket_id>.md`
   - Types: `feature`, `bugfix`, `doc`, `removal`, `misc`
   - Example: `feature.123.added-new-feature.md`

2. **Preview changelog**:
   ```bash
   uv run towncrier build --version X.Y.Z --draft
   ```

3. **Generate changelog**:
   ```bash
   uv run towncrier build --version X.Y.Z
   ```

4. **Clean up fragments** (after generating changelog):
   ```bash
   uv run towncrier build --version X.Y.Z --keep
   ```

### Github Actions

The template includes two Github Actions workflows.

The first one runs tests and linters on every push on the main and dev branches. You can find the workflow file in `.github/workflows/main-list-test.yml`.

The second one is triggered on every tag push and can also be triggered manually. It builds the distribution and uploads it to PyPI. You can find the workflow file in `.github/workflows/publish.yaml`.
