# Judge LLM Documentation

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## 🚀 Quick Start

### Installation

```bash
npm install
# or
yarn
```

### Local Development (Fast, No Search)

```bash
npm start
# or
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

**⚠️ Note:** Search functionality is **NOT available** in development mode.

### Production Build (With Search)

```bash
npm run build
# or
yarn build
```

This command generates static content into the `build` directory and includes the search index.

### Testing Locally With Search

```bash
# Build the site
npm run build

# Serve the production build
npm run serve
```

Now search will work at `http://localhost:3000`

## 🔍 Search Functionality

**Important:** The local search index is only generated during production builds:

- ✅ `npm run build` - Generates search index
- ❌ `npm start` - Does NOT generate search index (fast development)

To test search locally: `npm run build && npm run serve`

See [SEARCH.md](./SEARCH.md) for complete search documentation.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
