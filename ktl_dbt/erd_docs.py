import re
import subprocess
from typing import Any, Dict
import json
import os

from ktl_dbt.input_validators import DbtArtifactType, verify_and_read


def update_docs_with_render_dv_erd_macro(manifest: Dict[str, Any], target_dir):

    def run_dbt_operation(args):
        # Create the command to run
        command = f"dbt --quiet run-operation render_dv_erd_docs --args '{{models: [{args}]}}' --target-path '/tmp/.dbt'"
        
        # Execute the command and capture the output
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Command failed with error: {result.stdout}")
        
        return re.sub(r"( *\n)+", "\n\n", result.stdout)


    def diagram_to_svg(diagram, img_name):
        os.makedirs(target_dir / f"ktl_autovault_erd_images", exist_ok=True)
        mmd_path = target_dir / f"ktl_autovault_erd_images/{img_name}.mmd"
        svg_path = target_dir / f"ktl_autovault_erd_images/{img_name}.svg"

        with open(mmd_path, 'w') as f:
            f.write(diagram)
            f.close

        try:
            directory_path = os.path.dirname(os.path.abspath(__file__))
            subprocess.check_call(
                args=['mmdc', '-i', mmd_path, '-o', svg_path, '-p', f'{directory_path}/puppeteer-config.json'],
                stderr=subprocess.STDOUT,
                text=True
            )
        except Exception as e:
            print(e)


    replace_dict = dict()
    def insert_rendered_erds_in_doc_blocks(doc_block: str) -> str:

        pattern = re.compile(r'```render_dv_erd_docs\(([^)]*)\)```')

        def replacer(match):
            args = match.group(1).split(',')
            args.sort()
            args = ','.join(args)

            if args not in replace_dict:
                diagram = run_dbt_operation(args).strip()
                img_name = args.replace(',', '_')
                diagram_to_svg(diagram, img_name)

                replace_dict[args] = f"![{img_name}](ktl_autovault_erd_images/{img_name}.svg)"

            return replace_dict[args]
        
        # Replace the pattern with the command output
        return re.sub(pattern, replacer, doc_block)

    for k, v in manifest["nodes"].items():
        manifest["nodes"][k]["description"] = insert_rendered_erds_in_doc_blocks(
            v["description"]
        )

    for k, v in manifest["docs"].items():
        manifest["docs"][k]["block_contents"] = insert_rendered_erds_in_doc_blocks(
            v["block_contents"]
        )


def generate_erd_docs(target_dir, static_docs_page):
    manifest = verify_and_read(target_dir / "manifest.json", DbtArtifactType.MANIFEST)
    update_docs_with_render_dv_erd_macro(manifest, target_dir)

    with open(target_dir / "manifest.json", "w") as w_manifest:
        json.dump(manifest, w_manifest)

    # Mimic the behaviour of dbt docs generate --static.
    if static_docs_page:
        manifest = verify_and_read(target_dir / "manifest.json", DbtArtifactType.MANIFEST)
        catalog = verify_and_read(target_dir / "catalog.json", DbtArtifactType.CATALOG)
        
        # This setup comes straight from
        # https://github.com/mescanne/dbt-core/blob/e8c8eb2b7fc64e0db2817de0b538780d56c7fd99/core/dbt/task/generate.py#L280
        with open(target_dir / "index.html", "r") as index_html_handle:
            index_html = index_html_handle.read()
        
        index_html = index_html.replace('"MANIFEST.JSON INLINE DATA"', json.dumps(manifest))
        index_html = index_html.replace('"CATALOG.JSON INLINE DATA"', json.dumps(catalog))
        
        with open(target_dir / "index.html", "w") as s_index_html_handle:
            s_index_html_handle.write(index_html)
