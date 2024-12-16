import click
import subprocess
import sys
import os
import yaml
from pathlib import Path
import traceback

from ktl_dbt.autovault import load_ktl_autovault_configs
from ktl_dbt.erd_docs import generate_erd_docs


def exit_with_error(msg: str):
    click.secho(msg, fg="red")
    sys.exit(1)


@click.group()
def cli():
    pass


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument('dbt_args', nargs=-1, type=click.UNPROCESSED)
@click.option('-u', '--url', default=os.environ.get('KTL_AUTOVAULT_URL', 'http://192.168.1.53:18000/api/entity/?dataflow=15'))
def ktl_dbt(dbt_args, url):
    """ktl-dbt: A CLI application to run dbt commands."""
    
    list_docs_args = list(dbt_args)
    
    if list_docs_args[0] == "load-autovault-configs":
        load_ktl_autovault_configs(from_api=True, api_url=url)
        sys.exit(0)

    try:
        load_ktl_autovault_configs()
        subprocess.run(['dbt'] + [arg for arg in list_docs_args if arg != "--static"], check=True)

    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

    # generate dbt docs for dv ERD
    if list_docs_args[:2] == ["docs", "generate"]:
        click.echo("Finished generating dbt docs. Rendering ERD's and adding to docs blocks...")

        cli_target_path = next(
            iter([
                p for idx, p in enumerate(list_docs_args)
                if idx > 0 and list_docs_args[idx - 1] == "--target-path"
                    and p != "--target-path"
            ]),
            None,
        )
        
        env_target_path = os.environ.get("DBT_TARGET_PATH")

        with open(f"{os.environ.get('DBT_PROJECT_DIR', '.')}/dbt_project.yml", "r") as dbt_project_file:
            dbt_project_target_path = yaml.safe_load(dbt_project_file.read()).get(
                "target-path"
            )

        target_dir = Path(next(td
            for td in [
                cli_target_path,
                env_target_path,
                dbt_project_target_path,
                "./target",
            ]
            if td is not None
        ))

        static_docs_page = "--static" in list_docs_args

        try:
            generate_erd_docs(target_dir, static_docs_page)
            click.secho("All done.", fg="green")
        except Exception as e:
            traceback.print_exc()
            exit_with_error(e)


if __name__ == "__main__":
    cli()
