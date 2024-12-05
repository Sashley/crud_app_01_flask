from typing import Dict, List
from config import ModelConfig, FieldType, RelationType
import os
from jinja2 import Environment, DictLoader

class ModelGenerator:
    def __init__(self):
        self.model_template = Environment(loader=DictLoader({
            'model': '''
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class {{ config.name }}(Base):
    __tablename__ = '{{ config.table_name }}'
    
    {% for field in config.fields %}
    {{ field.name }} = Column({{ field.type.value }}{% if field.primary_key %}, primary_key=True{% endif %})
    {% endfor %}
    
    {% for relation in config.relations %}
    {% if relation.type == RelationType.ONE_TO_MANY %}
    {{ relation.name }} = relationship("{{ relation.target_model }}", back_populates="{{ relation.back_populates }}")
    {% endif %}
    {% endfor %}
'''
        }))
        
        self.route_template = Environment(loader=DictLoader({
            'route': '''
from flask import request, render_template, redirect, url_for
from database import db_session
from generated_models.{{ config.table_name }} import {{ config.name }}

def register_{{ config.table_name }}_routes(app):
    @app.route('/{{ config.table_name }}')
    def list_{{ config.table_name }}():
        items = {{ config.name }}.query.all()
        return render_template('{{ config.table_name }}/list.html', items=items)
        
    @app.route('/{{ config.table_name }}/new', methods=['GET', 'POST'])
    def create_{{ config.table_name }}():
        if request.method == 'POST':
            item = {{ config.name }}()
            {% for field in config.fields %}
            {% if not field.primary_key %}
            item.{{ field.name }} = request.form.get('{{ field.name }}')
            {% endif %}
            {% endfor %}
            db_session.add(item)
            db_session.commit()
            return redirect(url_for('list_{{ config.table_name }}'))
        return render_template('{{ config.table_name }}/form.html')
'''
        }))

    def generate_model(self, config: ModelConfig):
        template = self.model_template.get_template('model')
        model_content = template.render(config=config, RelationType=RelationType)
        
        # Create the model file
        model_path = os.path.join('generated_models', f'{config.table_name}.py')
        with open(model_path, 'w') as f:
            f.write(model_content)
            
    def generate_routes(self, config: ModelConfig):
        template = self.route_template.get_template('route')
        route_content = template.render(config=config)
        
        # Create the routes file
        route_path = os.path.join('generated_routes', f'{config.table_name}_routes.py')
        with open(route_path, 'w') as f:
            f.write(route_content)
