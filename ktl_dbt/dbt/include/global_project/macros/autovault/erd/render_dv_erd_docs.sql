{% macro render_erd_from_dv_config(model) -%}

    {%- set target = model.get('target_table').lower() -%}
    {%- set entity_type = model.get('target_entity_type').lower() -%}
    {%- set parent = model.get('parent_table', '').lower() -%}

    {%- if parent != '' and entity_type == 'sat' -%}
        {{ parent + " ||--o{ " + target }} : ""
    {% elif parent != '' and entity_type == 'lsat' -%}
        {{ parent + " ||--o{ " + target }} : ""
    {% endif -%}

    {% for column in model.get('columns') -%}
        {%- set parent = column.get('parent', '').lower() -%}
        {%- if parent != '' -%}
            {%- set foreign_key = column.get('target').lower() -%}
            {{ parent + " ||--o{ " + target }} : ""
        {%- endif %}
    {% endfor -%}

    {{ target }} {
        {% for column in model.get('columns') | selectattr('key_type', 'defined') -%}
            {%- set key_type = column.get('key_type').lower() -%}
            {%- set name = column.get('target').lower() -%}
            {%- set dtype = api.Column.translate_type(column.get('dtype', '')).lower() -%}

            {%- if key_type == 'hash_key_' + entity_type or (entity_type == 'lsat' and key_type == 'hash_key_sat') -%}
                {{ dtype }} {{ name }} PK
            {%- elif key_type[:9] == 'hash_key_' -%}
                {{ dtype }} {{ name }} FK
            {%- endif %}
        {% endfor %}
    }

{%- endmacro %}


{% macro render_dv_erd_docs(models) -%}

    {%- set erd -%}

    erDiagram

    {%- if models|length == 1 and models[0] == "all" %}
        {% for model in dv_config("all") -%}
            {{ render_erd_from_dv_config(model) }}
        {% endfor -%}
    {%- else %}
        {% for model_name in models -%}
            {{ render_erd_from_dv_config(dv_config(model_name)) }}
        {% endfor -%}
    {%- endif %}
    
    {%- endset -%}

    {%- do print(erd) -%}

{%- endmacro %}
