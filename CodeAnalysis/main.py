# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CLI entry point for CodeAnalysis.
# Date: 2026-05-29
# ---------------------------------------------------------------------------
"""
main.py
-------
CLI entry point for CodeAnalysis.

Usage examples
~~~~~~~~~~~~~~
  # Analyse a single GitHub repo (HTML + JSON reports)
  python main.py analyse --repo https://github.com/owner/repo

  # Analyse with business-context overrides
  python main.py analyse --repo owner/repo --users 50000 --revenue 1000000

  # Analyse every repo in a GitHub organisation (up to 20)
  python main.py portfolio --org my-org --limit 20

  # Analyse a local directory (no GitHub clone)
  python main.py analyse --local ./path/to/project
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table   import Table
from rich         import box

from config.settings    import REPORT_DIR
from core.analyzer      import CodeAnalyzer
from core.github_fetcher import GitHubFetcher
from reports.html_reporter import write_html
from reports.json_reporter import write_json

console = Console()


# Function: _setup_logging
def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level   = level,
        format  = "%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt = "%H:%M:%S",
    )


# Function: _print_result_table
def _print_result_table(result) -> None:
    """Pretty-print the analysis summary to the terminal."""
    table = Table(title=f"[bold cyan]CodeAnalysis – {result.repo_name}[/]",
                  box=box.ROUNDED, border_style="bright_black")

    table.add_column("Metric",     style="cyan",  no_wrap=True)
    table.add_column("Score",      style="white", justify="right")
    table.add_column("Risk Level", style="bold",  justify="center")

    # Function: risk_color
    def risk_color(label: str) -> str:
        if label in ("EXCELLENT", "GOOD", "LOW", "LOW RISK"):
            return f"[green]{label}[/green]"
        if label in ("FAIR", "MEDIUM", "MEDIUM RISK"):
            return f"[yellow]{label}[/yellow]"
        return f"[red]{label}[/red]"

    table.add_row("Software Health",
                  f"{result.health.health}/100",
                  risk_color(result.health.risk_label))
    table.add_row("  ↳ Resiliency",    f"{result.health.resiliency}/100", "")
    table.add_row("  ↳ Agility",       f"{result.health.agility}/100",    "")
    table.add_row("  ↳ Elegance",      f"{result.health.elegance}/100",   "")
    table.add_row("Technical Debt",
                  f"{result.debt.debt_months} PM / ${result.debt.debt_usd:,.0f}",
                  risk_color(result.debt.risk_label))
    table.add_row("  ↳ Debt Ratio",    f"{result.debt.debt_ratio}%",      "")
    table.add_row("  ↳ FTEs Needed",   str(result.debt.debt_ftes),        "")
    table.add_row("Cloud Maturity",
                  f"{result.cloud.total}/100",
                  risk_color(result.cloud.risk_label))
    table.add_row("OSS Safety",
                  f"{result.oss.total}/100",
                  risk_color(result.oss.risk_label))
    table.add_row("  ↳ Vulnerable",   str(result.oss.vulnerable_count),  "")
    table.add_row("  ↳ License issues", str(result.oss.license_issues),  "")
    table.add_row("Business Impact",
                  f"{result.impact.total}/100",
                  risk_color(result.impact.risk_label))

    console.print(table)

    # Languages table
    lang_table = Table(title="Language Breakdown",
                       box=box.SIMPLE, border_style="bright_black")
    lang_table.add_column("Language");   lang_table.add_column("Files", justify="right")
    lang_table.add_column("SLOC",       justify="right")
    lang_table.add_column("Avg CC",     justify="right")
    lang_table.add_column("Functions",  justify="right")
    lang_table.add_column("Classes",    justify="right")

    for r in result.language_reports:
        lang_table.add_row(
            r.language, str(r.file_count), str(r.total_sloc),
            f"{r.avg_complexity:.1f}", str(r.total_functions), str(r.total_classes)
        )
    console.print(lang_table)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

# Function: cli
@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx, verbose):
    """CodeAnalysis – Deep source code analysis platform."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    _setup_logging(verbose)


# Function: analyse
@cli.command()
@click.option("--repo",    "-r", default=None,
              help="GitHub repo URL or owner/repo slug.")
@click.option("--local",   "-l", default=None,
              help="Path to a local repository (skip GitHub fetch).")
@click.option("--users",   "-u", default=100, show_default=True,
              help="Estimated user count for Business Impact score.")
@click.option("--revenue", "-$", default=0.0, show_default=True,
              help="Estimated annual revenue impact (USD) for Business Impact.")
@click.option("--output",  "-o", default=str(REPORT_DIR), show_default=True,
              help="Directory to write reports into.")
@click.option("--format",  "-f",
              type=click.Choice(["html", "json", "both"], case_sensitive=False),
              default="both", show_default=True,
              help="Output report format.")
@click.pass_context
def analyse(ctx, repo, local, users, revenue, output, format):
    """Analyse a single repository."""
    verbose = ctx.obj.get("verbose", False)

    if not repo and not local:
        console.print("[red]Error:[/red] Provide --repo or --local.")
        sys.exit(1)

    output_dir = Path(output)
    repo_meta  = None

    if local:
        repo_path = Path(local).expanduser().resolve()
        if not repo_path.exists():
            console.print(f"[red]Path not found:[/red] {repo_path}")
            sys.exit(1)
        console.print(f"[cyan]Analysing local path:[/cyan] {repo_path}")
    else:
        console.print(f"[cyan]Fetching repository:[/cyan] {repo}")
        fetcher   = GitHubFetcher()
        repo_meta = fetcher.fetch_repo(repo)
        repo_path = repo_meta.local_path
        console.print(f"[green]✓[/green] Cloned to {repo_path}")

    console.print("[cyan]Running analysis …[/cyan]")
    result = CodeAnalyzer(
        repo_path  = repo_path,
        repo_meta  = repo_meta,
        users      = users,
        revenue    = revenue,
    ).run()

    _print_result_table(result)

    # Write reports
    if format in ("json", "both"):
        json_path = write_json(result, output_dir)
        console.print(f"[green]JSON report:[/green] {json_path}")

    if format in ("html", "both"):
        html_path = write_html(result, output_dir)
        console.print(f"[green]HTML report:[/green] {html_path}")


# Function: portfolio
@cli.command()
@click.option("--org",    "-o", required=True,
              help="GitHub organisation name.")
@click.option("--limit",  "-n", default=20, show_default=True,
              help="Maximum number of repos to analyse.")
@click.option("--output", "-d", default=str(REPORT_DIR), show_default=True,
              help="Directory to write reports into.")
@click.pass_context
def portfolio(ctx, org, limit, output):
    """Analyse all repositories in a GitHub organisation (portfolio view)."""
    output_dir = Path(output)
    fetcher    = GitHubFetcher()

    console.print(f"[cyan]Fetching organisation '{org}' (max {limit} repos) …[/cyan]")
    repos = fetcher.fetch_organisation(org, limit=limit)

    if not repos:
        console.print("[red]No repositories found.[/red]")
        sys.exit(1)

    console.print(f"[green]Found {len(repos)} repos. Analysing …[/green]\n")

    portfolio_table = Table(
        title   = f"Portfolio – {org}",
        box     = box.ROUNDED,
        border_style = "bright_black",
    )
    for col in ("Repo", "SLOC", "Health", "Debt PM", "Cloud", "OSS", "Impact", "Risk"):
        portfolio_table.add_column(col, justify="right" if col not in ("Repo",) else "left")

    for meta in repos:
        try:
            result = CodeAnalyzer(
                repo_path = meta.local_path,
                repo_meta = meta,
            ).run()

            # Write individual reports
            write_json(result, output_dir)
            write_html(result, output_dir)

            portfolio_table.add_row(
                meta.full_name,
                str(result.total_sloc),
                f"{result.health.health}",
                f"{result.debt.debt_months}",
                f"{result.cloud.total}",
                f"{result.oss.total}",
                f"{result.impact.total}",
                result.health.risk_label,
            )
        except Exception as exc:   # noqa: BLE001
            console.print(f"[yellow]Skipping {meta.full_name}: {exc}[/yellow]")

    console.print(portfolio_table)
    console.print(f"\n[green]Reports written to:[/green] {output_dir}")


if __name__ == "__main__":
    cli(obj={})
