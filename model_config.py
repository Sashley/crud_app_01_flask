from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class FieldType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATETIME = "datetime"
    FOREIGN_KEY = "foreign_key"

class RelationType(Enum):
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    ONE_TO_ONE = "one_to_one"

@dataclass
class Field:
    name: str
    field_type: FieldType
    nullable: bool = True
    foreign_key: Optional[str] = None
    relationship: Optional[RelationType] = None
    validation: Optional[Dict[str, Any]] = None

@dataclass
class ModelConfig:
    name: str
    table_name: str
    fields: List[Field]
    display_name: str
    menu_section: Optional[str] = None
    parent_model: Optional[str] = None
    list_display: Optional[List[str]] = None
    search_fields: Optional[List[str]] = None
    order_by: Optional[List[str]] = None

# Example configuration for Manifest
manifest_config = ModelConfig(
    name="Manifest",
    table_name="manifest",
    display_name="Shipping Manifest",
    menu_section="Shipping",
    fields=[
        Field("id", FieldType.INTEGER, nullable=False),
        Field("bill_of_lading", FieldType.STRING, nullable=True),
        Field("shipper_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="client.id", relationship=RelationType.MANY_TO_ONE),
        Field("consignee_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="client.id", relationship=RelationType.MANY_TO_ONE),
        Field("vessel_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="vessel.id", relationship=RelationType.MANY_TO_ONE),
        Field("voyage_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="voyage.id", relationship=RelationType.MANY_TO_ONE),
        Field("port_of_loading_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="port.id", relationship=RelationType.MANY_TO_ONE),
        Field("port_of_discharge_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="port.id", relationship=RelationType.MANY_TO_ONE),
        Field("place_of_delivery", FieldType.STRING, nullable=True),
        Field("place_of_receipt", FieldType.STRING, nullable=True),
        Field("clauses", FieldType.STRING, nullable=True),
        Field("date_of_receipt", FieldType.DATETIME, nullable=True),
        Field("manifester_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="user.id", relationship=RelationType.MANY_TO_ONE),
    ],
    list_display=["bill_of_lading", "shipper_id", "consignee_id", "vessel_id", "voyage_id"],
    search_fields=["bill_of_lading"],
    order_by=["-id"]
)

# Example configuration for LineItem
lineitem_config = ModelConfig(
    name="LineItem",
    table_name="lineitem",
    display_name="Line Item",
    menu_section="Shipping",
    parent_model="Manifest",
    fields=[
        Field("id", FieldType.INTEGER, nullable=False),
        Field("manifest_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="manifest.id", relationship=RelationType.MANY_TO_ONE),
        Field("description", FieldType.STRING, nullable=True),
        Field("quantity", FieldType.INTEGER, nullable=True),
        Field("weight", FieldType.INTEGER, nullable=True),
        Field("volume", FieldType.INTEGER, nullable=True),
        Field("pack_type_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="packtype.id", relationship=RelationType.MANY_TO_ONE),
        Field("commodity_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="commodity.id", relationship=RelationType.MANY_TO_ONE),
        Field("container_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="container.id", relationship=RelationType.MANY_TO_ONE),
        Field("manifester_id", FieldType.FOREIGN_KEY, nullable=True, foreign_key="user.id", relationship=RelationType.MANY_TO_ONE),
    ],
    list_display=["description", "quantity", "weight", "volume"],
    search_fields=["description"],
    order_by=["-id"]
)

# Registry of all model configurations
model_registry = {
    "manifest": manifest_config,
    "lineitem": lineitem_config,
}
