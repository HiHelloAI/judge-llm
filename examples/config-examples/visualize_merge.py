#!/usr/bin/env python3
"""
Example: Visual Configuration Merge

This example provides a visual side-by-side comparison showing which
values come from defaults and which are overridden by your config.
"""

import yaml
from pathlib import Path
from judge_llm.core.config_loader import get_loader


def color_text(text, color):
    """Add color to terminal text"""
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'gray': '\033[90m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def print_header(title):
    print("\n" + "=" * 120)
    print(f"  {title}")
    print("=" * 120)


def get_nested_value(config, path):
    """Get value from nested dict using dot notation path"""
    keys = path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and key.isdigit():
            idx = int(key)
            value = value[idx] if idx < len(value) else None
        else:
            return None
    return value


def main():
    print_header("VISUAL CONFIGURATION MERGE")

    # Load configurations
    loader = get_loader()
    default_config_path = Path.cwd().parent.parent / ".judge_llm.defaults.yaml"

    with open(default_config_path, 'r') as f:
        default_config = yaml.safe_load(f)

    with open("config-with-defaults.yaml", 'r') as f:
        user_config = yaml.safe_load(f)

    merged_config = loader.load(
        config="config-with-defaults.yaml",
        use_defaults=True
    )

    # Define config paths to compare
    config_paths = [
        ("agent.num_runs", "Number of runs"),
        ("agent.parallel_execution", "Parallel execution"),
        ("agent.max_workers", "Max workers"),
        ("agent.log_level", "Log level"),
        ("agent.fail_on_threshold_violation", "Fail on threshold violation"),
        ("agent.validate_config", "Validate config"),
        ("dataset.loader", "Dataset loader"),
        ("dataset.paths", "Dataset paths"),
        ("evaluators.0.threshold", "Evaluator threshold"),
        ("evaluators.0.enabled", "Evaluator enabled"),
    ]

    # Print header
    print()
    print(f"{'Config Path':<40} | {'Default Value':<25} | {'Your Value':<25} | {'Final Value':<25} | {'Source':<15}")
    print("-" * 140)

    for path, description in config_paths:
        default_val = get_nested_value(default_config, path)
        user_val = get_nested_value(user_config, path)
        merged_val = get_nested_value(merged_config, path)

        # Determine source and color
        if user_val is not None:
            source = color_text("YOUR CONFIG", "green")
            final_color = "green"
        else:
            source = color_text("DEFAULT", "blue")
            final_color = "blue"

        # Format values
        def format_val(v):
            if v is None:
                return color_text("-", "gray")
            elif isinstance(v, list):
                return str(v)[:23] + "..." if len(str(v)) > 25 else str(v)
            else:
                return str(v)

        default_str = format_val(default_val)
        user_str = format_val(user_val)
        merged_str = color_text(format_val(merged_val), final_color)

        print(f"{description:<40} | {default_str:<25} | {user_str:<25} | {merged_str:<25} | {source:<15}")

    # Legend
    print("\n" + "=" * 120)
    print("LEGEND:")
    print(f"  {color_text('GREEN', 'green')}  = Value from YOUR config (overrides default)")
    print(f"  {color_text('BLUE', 'blue')}   = Value from DEFAULT config (inherited)")
    print(f"  {color_text('GRAY', 'gray')}   = Not specified")
    print("=" * 120)

    # Visual diagram
    print_header("MERGE FLOW DIAGRAM")
    print()
    print("  ┌─────────────────────────────────────┐")
    print("  │   .judge_llm.defaults.yaml          │")
    print("  │   (Parent/Default Configuration)     │")
    print("  └──────────────┬──────────────────────┘")
    print("                 │")
    print("                 │  Provides base values")
    print("                 ▼")
    print("  ┌─────────────────────────────────────┐")
    print("  │         MERGE PROCESS               │")
    print("  │   1. Load default config            │")
    print("  │   2. Load your config               │")
    print("  │   3. Your values override defaults  │")
    print("  │   4. Missing values inherit         │")
    print("  └──────────────┬──────────────────────┘")
    print("                 │")
    print("                 ▼")
    print("  ┌─────────────────────────────────────┐")
    print("  │   config-with-defaults.yaml         │")
    print("  │   (Your Configuration - Overrides)   │")
    print("  └──────────────┬──────────────────────┘")
    print("                 │")
    print("                 │  Results in...")
    print("                 ▼")
    print("  ┌─────────────────────────────────────┐")
    print("  │      FINAL MERGED CONFIG            │")
    print("  │   Used by Judge LLM for evaluation  │")
    print("  └─────────────────────────────────────┘")
    print()

    print_header("KEY INSIGHTS")
    print()
    print("✅ You only need to specify values that differ from defaults")
    print("✅ Unspecified values automatically inherit from parent config")
    print("✅ Your values always take precedence over defaults")
    print("✅ This keeps your config files clean and maintainable")
    print()


if __name__ == "__main__":
    main()
