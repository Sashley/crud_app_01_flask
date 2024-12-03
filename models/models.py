from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Manifest(Base):
    __tablename__ = 'manifest'    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    bill_of_lading = Column(String, nullable=True)
    shipper_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    consignee_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=True)
    voyage_id = Column(Integer, ForeignKey("voyage.id"), nullable=True)
    port_of_loading_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    port_of_discharge_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    place_of_delivery = Column(String, nullable=True)
    place_of_receipt = Column(String, nullable=True)
    clauses = Column(String, nullable=True)
    date_of_receipt = Column(DateTime, nullable=True)
    manifester_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    line_items = relationship("LineItem", back_populates="manifest")
    vessel = relationship("Vessel", back_populates="manifests")
    voyage = relationship("Voyage", back_populates="manifests")
    shipper = relationship("Client", foreign_keys=[shipper_id])
    consignee = relationship("Client", foreign_keys=[consignee_id])
    port_of_loading = relationship("Port", foreign_keys=[port_of_loading_id])
    port_of_discharge = relationship("Port", foreign_keys=[port_of_discharge_id])


class LineItem(Base):
    __tablename__ = 'lineitem'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    manifest_id = Column(Integer, ForeignKey("manifest.id"), nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=True)
    pack_type_id = Column(Integer, ForeignKey("packtype.id"), nullable=True)
    commodity_id = Column(Integer, ForeignKey("commodity.id"), nullable=True)
    container_id = Column(Integer, ForeignKey("container.id"), nullable=True)
    manifester_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    manifest = relationship("Manifest", back_populates="line_items")
    pack_type = relationship("PackType", back_populates="line_items")
    commodity = relationship("Commodity", back_populates="line_items")
    container = relationship("Container", back_populates="line_items")

class Commodity(Base):
    __tablename__ = 'commodity'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    line_items = relationship("LineItem", back_populates="commodity")
    rates = relationship("Rate", back_populates="commodity")

class PackType(Base):
    __tablename__ = 'packtype'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    line_items = relationship("LineItem", back_populates="pack_type")
    rates = relationship("Rate", back_populates="pack_type")

class Container(Base):
    __tablename__ = 'container'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    number = Column(String, nullable=True)
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    updated = Column(DateTime, nullable=True)
    
    line_items = relationship("LineItem", back_populates="container")
    container_historys = relationship("ContainerHistory", back_populates="container")
    port = relationship("Port", back_populates="containers")

class ContainerHistory(Base):
    __tablename__ = 'containerhistory'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    container_id = Column(Integer, ForeignKey("container.id"), nullable=True)
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    container_status_id = Column(Integer, ForeignKey("containerstatus.id"), nullable=True)
    damage = Column(String, nullable=True)
    updated = Column(DateTime, nullable=True)

    container = relationship("Container", back_populates="container_historys")
    container_status = relationship("ContainerStatus", back_populates="container_histories")
    port = relationship("Port")
    client = relationship("Client")

class ContainerStatus(Base):
    __tablename__ = 'containerstatus'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    container_histories = relationship("ContainerHistory", back_populates="container_status")

class ShippingCompany(Base):
    __tablename__ = 'shippingcompany'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    
    vessels = relationship("Vessel", back_populates="shipping_company")

class Vessel(Base):
    __tablename__ = 'vessel'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    shipping_company_id = Column(Integer, ForeignKey("shippingcompany.id"), nullable=True)
    
    manifests = relationship("Manifest", back_populates="vessel")
    voyages = relationship("Voyage", back_populates="vessel")
    shipping_company = relationship("ShippingCompany", back_populates="vessels")

class Voyage(Base):
    __tablename__ = 'voyage'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=True)
    rotation_number = Column(Integer, nullable=True)
    
    vessel = relationship("Vessel", back_populates="voyages")
    legs = relationship("Leg", back_populates="voyage")
    manifests = relationship("Manifest", back_populates="voyage")

class Leg(Base):
    __tablename__ = 'leg'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    voyage_id = Column(Integer, ForeignKey("voyage.id"), nullable=True)
    port_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    leg_number = Column(Integer, nullable=True)
    eta = Column(DateTime, nullable=True)
    etd = Column(DateTime, nullable=True)
    
    voyage = relationship("Voyage", back_populates="legs")
    port = relationship("Port")

class Port(Base):
    __tablename__ = 'port'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=True)  # Fixed column name
    prefix = Column(String, nullable=True)
    
    containers = relationship("Container", back_populates="port")
    country = relationship("Country", back_populates="ports")

class PortPair(Base):
    __tablename__ = 'portpair'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    pol_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    pod_id = Column(Integer, ForeignKey("port.id"), nullable=True)
    distance = Column(Integer, nullable=True)
    
    port_of_loading = relationship("Port", foreign_keys=[pol_id])
    port_of_discharge = relationship("Port", foreign_keys=[pod_id])

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    
    ports = relationship("Port", back_populates="country")

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    address = Column(String, nullable=True)
    town = Column(String, nullable=True)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    shipped_manifests = relationship("Manifest", foreign_keys=[Manifest.shipper_id], back_populates="shipper")
    consigned_manifests = relationship("Manifest", foreign_keys=[Manifest.consignee_id], back_populates="consignee")
    rates = relationship("Rate", back_populates="client")
    country = relationship("Country")

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    
    line_items = relationship("LineItem")
    manifests = relationship("Manifest")

class Rate(Base):
    __tablename__ = 'rate'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    distance = Column(Integer, nullable=True)
    commodity_id = Column(Integer, ForeignKey("commodity.id"), nullable=True)
    pack_type_id = Column(Integer, ForeignKey("packtype.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=True)
    rate = Column(Float, nullable=True)
    effective = Column(DateTime, nullable=True)
    
    commodity = relationship("Commodity", back_populates="rates")
    pack_type = relationship("PackType", back_populates="rates")
    client = relationship("Client", back_populates="rates")