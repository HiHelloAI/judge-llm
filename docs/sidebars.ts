import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'installation',
    'quick-start',
    {
      type: 'category',
      label: 'Core Concepts',
      collapsed: false,
      items: [
        'core-concepts/overview',
        'core-concepts/architecture',
        'core-concepts/workflow',
        'core-concepts/data-models',
      ],
    },
    {
      type: 'category',
      label: 'User Guides',
      collapsed: false,
      items: [
        'guides/basic-usage',
        'guides/cli-reference',
        'guides/python-api',
        'guides/configuration',
        'guides/evalset-format',
        'guides/environment-variables',
        'guides/default-configs',
      ],
    },
    {
      type: 'category',
      label: 'Providers',
      items: [
        'providers/overview',
        'providers/gemini',
        'providers/mock',
        'providers/custom-providers',
      ],
    },
    {
      type: 'category',
      label: 'Evaluators',
      items: [
        'evaluators/overview',
        'evaluators/response-evaluator',
        'evaluators/trajectory-evaluator',
        'evaluators/cost-evaluator',
        'evaluators/latency-evaluator',
        'evaluators/custom-evaluators',
      ],
    },
    {
      type: 'category',
      label: 'Reporters',
      items: [
        'reporters/overview',
        'reporters/console-reporter',
        'reporters/html-reporter',
        'reporters/json-reporter',
        'reporters/database-reporter',
      ],
    },
    {
      type: 'category',
      label: 'Examples',
      collapsed: false,
      items: [
        'examples/overview',
        'examples/gemini-agent',
        'examples/default-config',
        'examples/custom-evaluator',
        'examples/safety-evaluation',
        'examples/config-override',
        'examples/database-tracking',
      ],
    },
    {
      type: 'category',
      label: 'Advanced Topics',
      items: [
        'advanced/parallel-execution',
        'advanced/per-test-overrides',
        'advanced/multi-turn-conversations',
        'advanced/safety-evaluation',
        'advanced/llm-as-judge',
        'advanced/performance-tuning',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api-reference/evaluate',
        'api-reference/base-classes',
        'api-reference/models',
        'api-reference/registry',
        'api-reference/utilities',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/development-setup',
        'contributing/code-style',
        'contributing/testing',
        'contributing/submitting-prs',
      ],
    },
  ],
};

export default sidebars;
