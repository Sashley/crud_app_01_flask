from typing import Dict, List
from jinja2 import Environment, FileSystemLoader
from .model_config import ModelConfig

def mock_url_for(*args, **kwargs):
    """Mock url_for function for template generation"""
    return '#'

class ModelGenerator:
    def __init__(self, configs: Dict[str, ModelConfig]):
        self.configs = configs
        self.jinja_env = Environment(loader=FileSystemLoader('generator/templates'))
        # Add mock url_for to template globals
        self.jinja_env.globals['url_for'] = mock_url_for
        
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
    {%- if field.field_type.value == 'foreign_key' %}
    {%- set related_table = field.foreign_key.split('.')[0] %}
    {%- set rel_name = get_relationship_name(field.name, related_table) %}
    {%- set class_name = related_table[0]|upper + related_table[1:] %}
    {{ rel_name }} = relationship("{{ class_name }}", foreign_keys=[{{ field.name }}])
    {%- endif %}
    {%- endfor %}

    def to_dict(self):
        return {
            {%- for field in config.fields %}
            '{{ field.name }}': getattr(self, '{{ field.name }}'),
            {%- endfor %}
            {%- for field in config.fields %}
            {%- if field.field_type.value == 'foreign_key' %}
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

    def get_relationship_name(self, field_name: str, related_table: str) -> str:
        """Generate relationship name from field name and related table"""
        if field_name.endswith('_id'):
            return field_name[:-3]
        return related_table

    def generate_route_module(self, config: ModelConfig) -> str:
        """Generate Flask route module code"""
        template = '''
from flask import Blueprint, render_template, request, redirect, url_for
from database import db_session
from generated_models.{{ config.table_name }} import {{ config.name }}

bp = Blueprint('{{ config.table_name }}', __name__)

def register_{{ config.table_name }}_routes(app):
    app.register_blueprint(bp)

@bp.route('/{{ config.table_name }}')
def list_{{ config.table_name }}():
    query = {{ config.name }}.query
    
    # Apply search filters
    search = request.args.get('search')
    if search:
        filters = []
        {%- for field in config.search_fields %}
        filters.append({{ config.name }}.{{ field }}.ilike(f'%{search}%'))
        {%- endfor %}
        if filters:
            query = query.filter(db.or_(*filters))
    
    # Apply sorting
    sort = request.args.get('sort', '{{ config.order_by[0] }}')
    if sort.startswith('-'):
        query = query.order_by(getattr({{ config.name }}, sort[1:]).desc())
    else:
        query = query.order_by(getattr({{ config.name }}, sort))
    
    items = query.all()
    return render_template(
        '{{ config.table_name }}/list.html',
        items=items,
        search=search,
        sort=sort
    )

@bp.route('/{{ config.table_name }}/new', methods=['GET', 'POST'])
def create_{{ config.table_name }}():
    if request.method == 'POST':
        item = {{ config.name }}()
        {%- for field in config.fields %}
        {%- if field.name != 'id' %}
        item.{{ field.name }} = request.form.get('{{ field.name }}')
        {%- endif %}
        {%- endfor %}
        
        db_session.add(item)
        db_session.commit()
        return redirect(url_for('{{ config.table_name }}.list_{{ config.table_name }}'))
    
    return render_template('{{ config.table_name }}/form.html')

@bp.route('/{{ config.table_name }}/<int:id>/edit', methods=['GET', 'POST'])
def edit_{{ config.table_name }}(id):
    item = {{ config.name }}.query.get_or_404(id)
    
    if request.method == 'POST':
        {%- for field in config.fields %}
        {%- if field.name != 'id' %}
        item.{{ field.name }} = request.form.get('{{ field.name }}')
        {%- endif %}
        {%- endfor %}
        
        db_session.commit()
        return redirect(url_for('{{ config.table_name }}.list_{{ config.table_name }}'))
    
    return render_template('{{ config.table_name }}/form.html', item=item)

@bp.route('/{{ config.table_name }}/<int:id>/delete', methods=['POST'])
def delete_{{ config.table_name }}(id):
    item = {{ config.name }}.query.get_or_404(id)
    db_session.delete(item)
    db_session.commit()
    return redirect(url_for('{{ config.table_name }}.list_{{ config.table_name }}'))
'''
        return self.jinja_env.from_string(template).render(config=config)

    def generate_list_template(self, config: ModelConfig) -> str:
        """Generate list view template"""
        template = '''{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>{{ config.display_name }} List</h1>
    
    <div class="row mb-3">
        <div class="col">
            <form method="get" class="form-inline">
                <div class="input-group">
                    <input type="text" name="search" class="form-control" 
                           placeholder="Search..." value="{{ search }}">
                    <div class="input-group-append">
                        <button type="submit" class="btn btn-primary">Search</button>
                    </div>
                </div>
            </form>
        </div>
        <div class="col-auto">
            <a href="{{ url_for(config.table_name + '.create_' + config.table_name) }}" 
               class="btn btn-success">Add New</a>
        </div>
    </div>

    <table class="table">
        <thead>
            <tr>
                {%- for field in config.list_display %}
                <th>
                    <a href="{{ url_for(config.table_name + '.list_' + config.table_name, sort=('-' + field if sort == field else field)) }}">
                        {{ field|title }}
                        {% if sort == field %}
                        <i class="fas fa-sort-up"></i>
                        {% elif sort == '-' + field %}
                        <i class="fas fa-sort-down"></i>
                        {% endif %}
                    </a>
                </th>
                {%- endfor %}
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                {%- for field in config.list_display %}
                <td>{{ item[field] }}</td>
                {%- endfor %}
                <td>
                    <a href="{{ url_for(config.table_name + '.edit_' + config.table_name, id=item.id) }}"
                       class="btn btn-sm btn-primary">Edit</a>
                    <form method="post" class="d-inline"
                          action="{{ url_for(config.table_name + '.delete_' + config.table_name, id=item.id) }}">
                        <button type="submit" class="btn btn-sm btn-danger" 
                                onclick="return confirm('Are you sure?')">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''
        return self.jinja_env.from_string(template).render(config=config)

    def generate_form_template(self, config: ModelConfig) -> str:
        """Generate form template"""
        template = '''{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>{% if item %}Edit{% else %}New{% endif %} {{ config.display_name }}</h1>
    
    <form method="post">
        {%- for field in config.fields %}
        {%- if field.name != 'id' %}
        <div class="form-group">
            <label for="{{ field.name }}">{{ field.name|title }}</label>
            <input type="text" class="form-control" id="{{ field.name }}" 
                   name="{{ field.name }}" value="{{ item[field.name] if item else '' }}">
        </div>
        {%- endif %}
        {%- endfor %}
        
        <button type="submit" class="btn btn-primary">Save</button>
        <a href="{{ url_for(config.table_name + '.list_' + config.table_name) }}" 
           class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}'''
        return self.jinja_env.from_string(template).render(config=config)

    def generate_all(self):
        """Generate all files for all models"""
        import os
        
        # Create output directories if they don't exist
        os.makedirs('generated_models', exist_ok=True)
        os.makedirs('generated_routes', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        
        # Generate files for each model
        for config in self.configs.values():
            # Create model directory
            os.makedirs(f'templates/{config.table_name}', exist_ok=True)
            
            # Generate model class
            model_code = self.generate_model_class(config)
            with open(f'generated_models/{config.table_name}.py', 'w') as f:
                f.write(model_code)
            
            # Generate route module
            route_code = self.generate_route_module(config)
            with open(f'generated_routes/{config.table_name}_routes.py', 'w') as f:
                f.write(route_code)
            
            # Generate templates
            list_template = self.generate_list_template(config)
            with open(f'templates/{config.table_name}/list.html', 'w') as f:
                f.write(list_template)
            
            form_template = self.generate_form_template(config)
            with open(f'templates/{config.table_name}/form.html', 'w') as f:
                f.write(form_template)
