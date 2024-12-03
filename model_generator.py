from typing import Dict, List
from model_config import ModelConfig, FieldType, RelationType
import os
from jinja2 import Environment, DictLoader

class ModelGenerator:
    def __init__(self, model_registry: Dict[str, ModelConfig]):
        self.model_registry = model_registry
        self.jinja_env = Environment(loader=DictLoader({
            'base.html': '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{% block title %}{% endblock %}</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <script src="https://unpkg.com/htmx.org@1.9.6"></script>
            </head>
            <body>
                {% block content %}{% endblock %}
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            '''
        }))

    def get_relationship_name(self, field_name: str, related_table: str) -> str:
        """Get the appropriate relationship name based on field and table names"""
        if field_name == 'shipper_id':
            return 'shipper'
        elif field_name == 'consignee_id':
            return 'consignee'
        elif field_name == 'port_of_loading_id':
            return 'port_of_loading'
        elif field_name == 'port_of_discharge_id':
            return 'port_of_discharge'
        elif field_name == 'manifester_id':
            return 'manifester'
        else:
            return related_table

    def generate_model_class(self, config: ModelConfig) -> str:
        """Generate SQLAlchemy model class code"""
        template = '''
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class {{ config.name }}(Base):
    __tablename__ = '{{ config.table_name }}'
    
    {%- for field in config.fields %}
    {% if field.name == 'id' %}
    {{ field.name }} = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    {%- elif field.field_type.value == 'foreign_key' %}
    {{ field.name }} = Column(Integer, ForeignKey("{{ field.foreign_key }}"), nullable={{ field.nullable }})
    {%- elif field.field_type.value == 'string' %}
    {{ field.name }} = Column(String, nullable={{ field.nullable }})
    {%- elif field.field_type.value == 'integer' %}
    {{ field.name }} = Column(Integer, nullable={{ field.nullable }})
    {%- elif field.field_type.value == 'float' %}
    {{ field.name }} = Column(Float, nullable={{ field.nullable }})
    {%- elif field.field_type.value == 'datetime' %}
    {{ field.name }} = Column(DateTime, nullable={{ field.nullable }})
    {%- endif %}
    {%- endfor %}

    # Relationships
    {%- for field in config.fields %}
    {%- if field.field_type.value == 'foreign_key' and field.relationship %}
    {%- set related_table = field.foreign_key.split('.')[0] %}
    {%- set rel_name = get_relationship_name(field.name, related_table) %}
    {%- if field.relationship.value == 'many_to_one' %}
    {{ rel_name }} = relationship("{{ related_table|title }}", foreign_keys=[{{ field.name }}])
    {%- elif field.relationship.value == 'one_to_many' %}
    {{ rel_name }}s = relationship("{{ related_table|title }}", back_populates="{{ config.table_name }}")
    {%- endif %}
    {%- endif %}
    {%- endfor %}

    def to_dict(self):
        return {
            {%- for field in config.fields %}
            '{{ field.name }}': getattr(self, '{{ field.name }}'),
            {%- endfor %}
            {%- for field in config.fields %}
            {%- if field.field_type.value == 'foreign_key' and field.relationship %}
            {%- set related_table = field.foreign_key.split('.')[0] %}
            {%- set rel_name = get_relationship_name(field.name, related_table) %}
            '{{ rel_name }}': getattr(self, '{{ rel_name }}').to_dict() if getattr(self, '{{ rel_name }}') else None,
            {%- endif %}
            {%- endfor %}
        }
'''
        return self.jinja_env.from_string(template).render(
            config=config,
            get_relationship_name=self.get_relationship_name
        )

    def generate_route_handler(self, config: ModelConfig) -> str:
        """Generate Flask route handler code"""
        template = '''
from flask import request, render_template, redirect, url_for
from database import db_session
from generated_models.{{ config.table_name }} import {{ config.name }}

def register_{{ config.table_name }}_routes(app):
    @app.route('/{{ config.table_name }}')
    def list_{{ config.table_name }}():
        offset = int(request.args.get('offset', 0))
        query = request.args.get('query', '')
        items = search_{{ config.table_name }}(query, offset, config.RECORDS_PER_PAGE) if query else get_{{ config.table_name }}(offset, config.RECORDS_PER_PAGE)
        return render_template('{{ config.table_name }}/list.html', 
            items=items,
            records_per_page=config.RECORDS_PER_PAGE
        )

    @app.route('/{{ config.table_name }}/create', methods=['GET', 'POST'])
    def create_{{ config.table_name }}():
        if request.method == 'POST':
            {%- for field in config.fields %}
            {%- if field.name != 'id' %}
            {%- if field.field_type.value == 'integer' %}
            {{ field.name }} = int(request.form['{{ field.name }}']) if request.form['{{ field.name }}'] else None
            {%- elif field.field_type.value == 'float' %}
            {{ field.name }} = float(request.form['{{ field.name }}']) if request.form['{{ field.name }}'] else None
            {%- else %}
            {{ field.name }} = request.form['{{ field.name }}'] if request.form['{{ field.name }}'] else None
            {%- endif %}
            {%- endif %}
            {%- endfor %}
            
            new_item = {{ config.name }}(
                {%- for field in config.fields %}
                {%- if field.name != 'id' %}
                {{ field.name }}={{ field.name }},
                {%- endif %}
                {%- endfor %}
            )
            db_session.add(new_item)
            db_session.commit()
            return redirect(url_for('list_{{ config.table_name }}'))
        
        # Get related data for dropdowns
        {%- for field in config.fields %}
        {%- if field.field_type.value == 'foreign_key' %}
        {%- set related_table = field.foreign_key.split('.')[0] %}
        {{ related_table }}s = db_session.query({{ related_table|title }}).all()
        {%- endif %}
        {%- endfor %}
        
        return render_template('{{ config.table_name }}/form.html', 
            mode='create',
            {%- for field in config.fields %}
            {%- if field.field_type.value == 'foreign_key' %}
            {%- set related_table = field.foreign_key.split('.')[0] %}
            {{ related_table }}s={{ related_table }}s,
            {%- endif %}
            {%- endfor %}
        )

    @app.route('/{{ config.table_name }}/<int:id>/edit', methods=['GET', 'POST'])
    def edit_{{ config.table_name }}(id):
        item = db_session.get({{ config.name }}, id)
        if not item:
            return "Not found", 404
            
        if request.method == 'POST':
            {%- for field in config.fields %}
            {%- if field.name != 'id' %}
            {%- if field.field_type.value == 'integer' %}
            item.{{ field.name }} = int(request.form['{{ field.name }}']) if request.form['{{ field.name }}'] else None
            {%- elif field.field_type.value == 'float' %}
            item.{{ field.name }} = float(request.form['{{ field.name }}']) if request.form['{{ field.name }}'] else None
            {%- else %}
            item.{{ field.name }} = request.form['{{ field.name }}'] if request.form['{{ field.name }}'] else None
            {%- endif %}
            {%- endif %}
            {%- endfor %}
            
            db_session.commit()
            return redirect(url_for('list_{{ config.table_name }}'))
        
        # Get related data for dropdowns
        {%- for field in config.fields %}
        {%- if field.field_type.value == 'foreign_key' %}
        {%- set related_table = field.foreign_key.split('.')[0] %}
        {{ related_table }}s = db_session.query({{ related_table|title }}).all()
        {%- endif %}
        {%- endfor %}
        
        return render_template('{{ config.table_name }}/form.html', 
            item=item,
            mode='edit',
            {%- for field in config.fields %}
            {%- if field.field_type.value == 'foreign_key' %}
            {%- set related_table = field.foreign_key.split('.')[0] %}
            {{ related_table }}s={{ related_table }}s,
            {%- endif %}
            {%- endfor %}
        )

    @app.route('/{{ config.table_name }}/<int:id>/delete', methods=['POST'])
    def delete_{{ config.table_name }}(id):
        item = db_session.get({{ config.name }}, id)
        if item:
            db_session.delete(item)
            db_session.commit()
        return redirect(url_for('list_{{ config.table_name }}'))

    def get_{{ config.table_name }}(offset, limit):
        return db_session.query({{ config.name }}).order_by(
            {%- for field in config.order_by %}
            {{ config.name }}.{{ field.lstrip('-') }}{{ '.desc()' if field.startswith('-') else '' }},
            {%- endfor %}
        ).offset(offset).limit(limit).all()

    def search_{{ config.table_name }}(query, offset, limit):
        search_term = f"%{query}%"
        return db_session.query({{ config.name }})\\
            {%- for field in config.search_fields %}
            {%- if not '__' in field %}
            .filter({{ config.name }}.{{ field }}.ilike(search_term))\\
            {%- endif %}
            {%- endfor %}
            .order_by({{ config.name }}.id.desc())\\
            .offset(offset)\\
            .limit(limit)\\
            .all()
'''
        return self.jinja_env.from_string(template).render(config=config)

    def generate_list_template(self, config: ModelConfig) -> str:
        """Generate list view template"""
        template = '''
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>{{ config.display_name }}</h1>
    
    <div class="mb-3">
        <input type="text" 
               class="form-control" 
               placeholder="Search..." 
               hx-get="/{{ config.table_name }}/search"
               hx-trigger="keyup changed delay:500ms"
               hx-target="#items-table">
    </div>

    <div class="mb-3">
        <a href="{{ '{{' }} url_for('create_{{ config.table_name }}') {{ '}}' }}" 
           class="btn btn-primary">Create New</a>
    </div>

    <div id="items-table">
        <table class="table">
            <thead>
                <tr>
                    {%- for field in config.list_display %}
                    <th>{{ field|title }}</th>
                    {%- endfor %}
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {{ '{% for item in items %}' }}
                <tr>
                    {%- for field in config.list_display %}
                    <td>{{ '{{' }} item.{{ field }} {{ '}}' }}</td>
                    {%- endfor %}
                    <td>
                        <a href="{{ '{{' }} url_for('edit_{{ config.table_name }}', id=item.id) {{ '}}' }}"
                           class="btn btn-sm btn-primary">Edit</a>
                        <form action="{{ '{{' }} url_for('delete_{{ config.table_name }}', id=item.id) {{ '}}' }}"
                              method="POST"
                              style="display: inline;">
                            <button type="submit" 
                                    class="btn btn-sm btn-danger"
                                    onclick="return confirm('Are you sure?')">Delete</button>
                        </form>
                    </td>
                </tr>
                {{ '{% endfor %}' }}
            </tbody>
        </table>
        
        <div hx-get="/{{ config.table_name }}/load_more?offset={{ '{{' }} items|length {{ '}}' }}"
             hx-trigger="revealed"
             hx-swap="afterend">
        </div>
    </div>
</div>
{% endblock %}
'''
        return self.jinja_env.from_string(template).render(config=config)

    def generate_form_template(self, config: ModelConfig) -> str:
        """Generate form template for create/edit"""
        template = '''
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>{{ '{{' }} mode|title {{ '}}' }} {{ config.display_name }}</h1>
    
    <form method="POST">
        {%- for field in config.fields %}
        {%- if field.name != 'id' %}
        <div class="mb-3">
            <label for="{{ field.name }}" class="form-label">{{ field.name|title }}</label>
            {%- if field.field_type.value == 'foreign_key' %}
            <select class="form-control" id="{{ field.name }}" name="{{ field.name }}" {{ '' if field.nullable else 'required' }}>
                <option value="">Select {{ field.name|title }}</option>
                {%- set related_table = field.foreign_key.split('.')[0] %}
                {{ '{% for ' + related_table + ' in ' + related_table + 's %}' }}
                <option value="{{ '{{' }} {{ related_table }}.id {{ '}}' }}"
                        {{ '{% if item and item.' + field.name + ' == ' + related_table + '.id %}selected{% endif %}' }}>
                    {{ '{{' }} {{ related_table }}.name {{ '}}' }}
                </option>
                {{ '{% endfor %}' }}
            </select>
            {%- else %}
            <input type="
                {%- if field.field_type.value == 'integer' or field.field_type.value == 'float' -%}
                number
                {%- elif field.field_type.value == 'datetime' -%}
                datetime-local
                {%- else -%}
                text
                {%- endif -%}"
                   class="form-control"
                   id="{{ field.name }}"
                   name="{{ field.name }}"
                   value="{{ '{{' }} item.{{ field.name }} if item else '' {{ '}}' }}"
                   {{ '' if field.nullable else 'required' }}>
            {%- endif %}
        </div>
        {%- endif %}
        {%- endfor %}
        
        <button type="submit" class="btn btn-primary">Save</button>
        <a href="{{ '{{' }} url_for('list_{{ config.table_name }}') {{ '}}' }}" 
           class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}
'''
        return self.jinja_env.from_string(template).render(config=config)

    def generate_all(self):
        """Generate all necessary files for all models"""
        # Create necessary directories
        os.makedirs('generated_models', exist_ok=True)
        os.makedirs('generated_routes', exist_ok=True)
        os.makedirs('templates/generators', exist_ok=True)
        
        for config in self.model_registry.values():
            # Generate model
            model_code = self.generate_model_class(config)
            with open(f'generated_models/{config.table_name}.py', 'w') as f:
                f.write(model_code)
            
            # Generate route handler
            route_code = self.generate_route_handler(config)
            with open(f'generated_routes/{config.table_name}_routes.py', 'w') as f:
                f.write(route_code)
            
            # Create template directory for this model
            template_dir = f'templates/{config.table_name}'
            os.makedirs(template_dir, exist_ok=True)
            
            # Generate templates
            with open(f'{template_dir}/list.html', 'w') as f:
                f.write(self.generate_list_template(config))
            
            with open(f'{template_dir}/form.html', 'w') as f:
                f.write(self.generate_form_template(config))

if __name__ == '__main__':
    from model_config import model_registry
    generator = ModelGenerator(model_registry)
    generator.generate_all()
