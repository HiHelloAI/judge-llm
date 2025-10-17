#!/usr/bin/env python3
"""
Example: Visualizing Configuration Merging

This example shows how the parent config (.judge_llm.defaults.yaml) is
merged with your actual config file to produce the final configuration.
"""

import yaml
from pathlib import Path
from judge_llm.core.config_loader import get_loader


def print_section(title):
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100 + "\n")


def print_yaml(config, indent=0):
    """Pretty print YAML configuration"""
    yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
    for line in yaml_str.split('\n'):
        if line.strip():
            print('  ' * indent + line)


def main():
    print_section("CONFIGURATION MERGING DEMONSTRATION")

    # Load the default configuration
    loader = get_loader()
    default_config_path = Path.cwd().parent.parent / ".judge_llm.defaults.yaml"

    print(f"📂 Default config location: {default_config_path}\n")

    # Read default config
    with open(default_config_path, 'r') as f:
        default_config = yaml.safe_load(f)

    # Read user config (minimal)
    user_config_path = "config-with-defaults.yaml"
    with open(user_config_path, 'r') as f:
        user_config = yaml.safe_load(f)

    # Load merged config using the loader
    merged_config = loader.load(
        config=user_config_path,
        use_defaults=True
    )

    # Display Step 1: Default Configuration
    print_section("STEP 1: Default Configuration (.judge_llm.defaults.yaml)")
    print("These are the base defaults that ship with Judge LLM:\n")
    print_yaml(default_config)

    # Display Step 2: User Configuration
    print_section("STEP 2: Your Configuration (config-with-defaults.yaml)")
    print("This is your minimal config - only what you want to override:\n")
    print_yaml(user_config)

    # Display Step 3: Merged Configuration
    print_section("STEP 3: Final Merged Configuration")
    print("This is what Judge LLM actually uses (defaults + your overrides):\n")
    print_yaml(merged_config)

    # Show specific examples of merging
    print_section("MERGING EXAMPLES")

    # Agent config merging
    print("🔹 AGENT CONFIGURATION:")
    print(f"   Default log_level:     {default_config.get('agent', {}).get('log_level', 'N/A')}")
    print(f"   Your config:           {user_config.get('agent', {}).get('log_level', 'Not specified (inherits default)')}")
    print(f"   ➜ Final value:         {merged_config.get('agent', {}).get('log_level')}")
    print()

    print(f"   Default num_runs:      {default_config.get('agent', {}).get('num_runs', 'N/A')}")
    print(f"   Your config:           {user_config.get('agent', {}).get('num_runs', 'Not specified (inherits default)')}")
    print(f"   ➜ Final value:         {merged_config.get('agent', {}).get('num_runs')}")
    print()

    print(f"   Default parallel:      {default_config.get('agent', {}).get('parallel_execution', 'N/A')}")
    print(f"   Your config:           {user_config.get('agent', {}).get('parallel_execution', 'Not specified (inherits default)')}")
    print(f"   ➜ Final value:         {merged_config.get('agent', {}).get('parallel_execution')}")
    print()

    # Dataset config - overridden
    print("🔹 DATASET CONFIGURATION:")
    print(f"   Default paths:         {default_config.get('dataset', {}).get('paths', 'N/A')}")
    print(f"   Your config:           {user_config.get('dataset', {}).get('paths', 'N/A')}")
    print(f"   ➜ Final value:         {merged_config.get('dataset', {}).get('paths')}")
    print("   ℹ️  Your value OVERRIDES the default")
    print()

    # Evaluators - partial merge
    print("🔹 EVALUATOR CONFIGURATION:")
    default_eval = default_config.get('evaluators', [{}])[0] if default_config.get('evaluators') else {}
    user_eval = user_config.get('evaluators', [{}])[0] if user_config.get('evaluators') else {}
    merged_eval = merged_config.get('evaluators', [{}])[0] if merged_config.get('evaluators') else {}

    print(f"   Default threshold:     {default_eval.get('threshold', 'N/A')}")
    print(f"   Your config:           {user_eval.get('threshold', 'Not specified (inherits default)')}")
    print(f"   ➜ Final value:         {merged_eval.get('threshold', 'N/A')}")
    print()

    print(f"   Default enabled:       {default_eval.get('enabled', 'N/A')}")
    print(f"   Your config:           {user_eval.get('enabled', 'Not specified (inherits default)')}")
    print(f"   ➜ Final value:         {merged_eval.get('enabled', 'N/A')}")
    print()

    # Show what happens with use_defaults=False
    print_section("COMPARISON: With vs Without Defaults")

    print("🔸 WITH DEFAULTS (use_defaults=True):")
    print(f"   Agent runs:            {merged_config.get('agent', {}).get('num_runs')}")
    print(f"   Agent parallel:        {merged_config.get('agent', {}).get('parallel_execution')}")
    print(f"   Agent log_level:       {merged_config.get('agent', {}).get('log_level')}")
    print()

    # Load without defaults
    config_no_defaults = loader.load(
        config=user_config_path,
        use_defaults=False
    )

    print("🔸 WITHOUT DEFAULTS (use_defaults=False):")
    print(f"   Agent runs:            {config_no_defaults.get('agent', {}).get('num_runs', 'Not set')}")
    print(f"   Agent parallel:        {config_no_defaults.get('agent', {}).get('parallel_execution', 'Not set')}")
    print(f"   Agent log_level:       {config_no_defaults.get('agent', {}).get('log_level', 'Not set')}")
    print()

    print("ℹ️  Notice: Without defaults, unspecified values are missing!")
    print()

    # Summary
    print_section("SUMMARY")
    print("✅ Default config provides base values for all settings")
    print("✅ Your config overrides specific values you want to change")
    print("✅ Unspecified values in your config inherit from defaults")
    print("✅ The merge happens automatically when use_defaults=True")
    print("✅ You can disable merging with use_defaults=False")
    print()
    print("💡 TIP: Use defaults to keep your configs clean and maintainable!")


if __name__ == "__main__":
    main()
