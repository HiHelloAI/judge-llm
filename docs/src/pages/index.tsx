import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <img
          src="/img/logo.png"
          alt="Judge LLM Logo"
          className={styles.logo}
        />
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started 🚀
          </Link>
          <Link
            className="button button--outline button--lg"
            to="/docs/examples/overview">
            View Examples 💡
          </Link>
        </div>
      </div>
    </header>
  );
}

function DemoSection() {
  return (
    <section className={styles.demoSection}>
      <div className="container">
        <Heading as="h2">
          See It In Action
        </Heading>
        <div style={{textAlign: 'center'}}>
          <img
            src="/img/demo.gif"
            alt="Judge LLM Demo"
            className={styles.demoImage}
          />
        </div>
      </div>
    </section>
  );
}

function QuickStartSection() {
  return (
    <section className={styles.quickStartSection}>
      <div className="container">
        <div className="row">
          <div className="col col--6">
            <Heading as="h3">CLI Usage</Heading>
            <pre className={styles.codeBlock}>
              <code>{`# Run evaluation
judge-llm run --config config.yaml

# List providers
judge-llm list providers

# Generate dashboard
judge-llm dashboard --db results.db`}</code>
            </pre>
          </div>
          <div className="col col--6">
            <Heading as="h3">Python API</Heading>
            <pre className={styles.codeBlock}>
              <code>{`from judge_llm import evaluate

report = evaluate(
    config="config.yaml"
)

print(f"Success: {report.success_rate:.1%}")`}</code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Evaluate and Compare LLM Providers`}
      description="A lightweight, extensible framework for evaluating and comparing LLM providers with systematic testing, cost tracking, and comprehensive reporting.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <DemoSection />
        <QuickStartSection />
      </main>
    </Layout>
  );
}
