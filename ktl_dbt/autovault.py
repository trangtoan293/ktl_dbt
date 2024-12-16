import os
import requests
import yaml


def load_ktl_autovault_configs_from_api(config_dir, api_url):
    response = requests.get(api_url)

    data = response.json()
    types = ['hub', 'sat', 'lnk', 'lsat']

    for key, properties in data.items():
        if key in types:
            for x in properties:
                os.makedirs(os.path.join(config_dir, key), exist_ok=True)

                with open(os.path.join(config_dir, key, x['name']+'.yml'), 'w') as f:
                    yaml.dump(x['properties'], f, default_flow_style=False)
                    f.close()


def load_ktl_autovault_configs(from_api=False, api_url=None):
    dbt_project_dir = os.getenv('DBT_PROJECT_DIR', '.')
    config_dir = os.path.join(dbt_project_dir, 'ktl_autovault_configs')
    macro_dir = os.path.join(dbt_project_dir, 'macros', 'ktl_autovault_configs')
    
    if from_api:
        os.makedirs(config_dir, exist_ok=True)
        load_ktl_autovault_configs_from_api(config_dir, api_url)
    
    if not os.path.exists(config_dir):
        return
    
    os.makedirs(macro_dir, exist_ok=True)

    for root, _, files in os.walk(config_dir):
        for file in files:
            if file.endswith('.yml'):
                yml_file = os.path.join(root, file)
                process_yaml_config_file(yml_file, macro_dir)
    
    create_dv_config_macro(config_dir, macro_dir)


def process_yaml_config_file(yml_file, macro_dir):
    filename = os.path.basename(yml_file).rsplit('.', 1)[0]
    new_file = os.path.join(macro_dir, f"{filename}_dv_config.sql")
    
    with open(yml_file, 'r') as yf:
        yml_content = yf.read()

    new_content = f"""

{{%- macro {filename}_dv_config() -%}}
    {{%- set model_yml -%}}

{yml_content}

    {{%- endset -%}}

    {{%- set model = fromyaml(model_yml) -%}}
    {{{{ return(model) }}}}

{{%- endmacro -%}}

"""
    with open(new_file, 'w') as nf:
        nf.write(new_content)


def create_dv_config_macro(config_dir, macro_dir):
    output_file = os.path.join(macro_dir, 'dv_config.sql')
    
    with open(output_file, 'w') as of:
        
        of.write("""
{%- macro dv_config(model_name) -%}
    
    {%- set all = [] -%}
""")

        for root, _, files in os.walk(config_dir):
            for file in files:
                if file.endswith('.yml'):
                    filename = os.path.basename(file).rsplit('.', 1)[0]
                    of.write(f"""
    {{%- if model_name=="{filename}" -%}}
        {{{{ return({filename}_dv_config()) }}}}
    {{%- endif -%}}
    {{%- do all.append({filename}_dv_config()) -%}}
""")

        of.write("""
    {%- if model_name=="all" -%}
        {{ return(all) }}
    {%- endif -%}
                 
    {{ exceptions.raise_compiler_error("Not found model '" + model_name + "', please ensure it is defined in directory 'ktl_autovault_configs' and rerun 'ktl-dbt load-autovault-configs'.") }}

{%- endmacro -%}
""")
