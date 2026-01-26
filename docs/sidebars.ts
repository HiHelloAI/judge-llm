import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    'application-overview',
    {
      type: 'category',
      label: 'Quick Start',
      collapsed: false,
      items: [
        'tutorial-basics/installation',
        'tutorial-basics/first-evaluation',
        'tutorial-basics/using-python-api',
        'tutorial-basics/comparing-models',
        'tutorial-basics/next-steps',
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
      label: 'Providers',
      items: [
        'providers/overview',
        'providers/gemini-provider',
        'providers/mock-provider',
        'providers/google-adk-provider',
        'providers/adk-http-provider',
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
        'evaluators/embedding-similarity-evaluator',
        'evaluators/llm-judge-evaluator',
        'evaluators/subagent-evaluator',
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
        'reporters/custom-reporters',
      ],
    },
  ],
};

export default sidebars;
