import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Judge LLM',
  tagline: 'A lightweight, extensible framework for evaluating and comparing LLM providers',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://judge-llm.dev',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'yourusername', // Usually your GitHub org/user name.
  projectName: 'judge-llm', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/yourusername/judge-llm/tree/main/docs/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        // Options for local search
        hashed: true,
        language: ['en'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
        indexDocs: true,
        indexBlog: false,
        indexPages: false,
        docsRouteBasePath: '/docs',
        // Search placeholder text
        searchBarShortcutHint: true,
        searchBarPosition: 'right',
      },
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/logo.png',
    metadata: [
      {name: 'keywords', content: 'llm, evaluation, testing, ai, machine learning, gemini, openai, anthropic, quality assurance'},
      {name: 'description', content: 'Judge LLM is a lightweight Python framework for evaluating and comparing LLM providers with support for quality gates, parallel execution, and comprehensive reporting'},
      {name: 'og:type', content: 'website'},
      {name: 'twitter:card', content: 'summary_large_image'},
    ],
    colorMode: {
      respectPrefersColorScheme: true,
    },
    // Algolia search (optional - uncomment and configure if you want to use Algolia instead of local search)
    // algolia: {
    //   appId: 'YOUR_APP_ID',
    //   apiKey: 'YOUR_SEARCH_API_KEY',
    //   indexName: 'judge-llm',
    //   contextualSearch: true,
    //   searchParameters: {},
    // },
    navbar: {
      title: 'Judge LLM',
      logo: {
        alt: 'Judge LLM Logo',
        src: 'img/logo.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Examples',
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'API',
        },
        {
          href: 'https://github.com/yourusername/judge-llm',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'Quick Start',
              to: '/docs/tutorial-basics/installation',
            },
            {
              label: 'Examples',
              to: '/docs/examples/overview',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'User Guides',
              to: '/docs/guides/basic-usage',
            },
            {
              label: 'Evaluators',
              to: '/docs/evaluators/overview',
            },
            {
              label: 'Reporters',
              to: '/docs/reporters/overview',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/yourusername/judge-llm',
            },
            {
              label: 'Issues',
              href: 'https://github.com/yourusername/judge-llm/issues',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Judge LLM. Licensed under CC BY-NC-SA 4.0.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml', 'json', 'typescript', 'javascript'],
      magicComments: [
        {
          className: 'theme-code-block-highlighted-line',
          line: 'highlight-next-line',
          block: {start: 'highlight-start', end: 'highlight-end'},
        },
        {
          className: 'code-block-error-line',
          line: 'error-next-line',
        },
      ],
    },
    // Code block features
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
