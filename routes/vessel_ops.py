from flask import Blueprint, render_template
from datetime import datetime
from database import db_session
from generated_models.vessel import Vessel
from generated_models.voyage import Voyage
from generated_models.leg import Leg
from generated_models.port import Port
from generated_models.shippingcompany import ShippingCompany
from generated_models.manifest import Manifest
from sqlalchemy import func, distinct

vessel_ops = Blueprint('vessel_ops', __name__)

@vessel_ops.route('/vessel-ops')
def dashboard():
    return render_template('vessel_ops/dashboard.html')

@vessel_ops.route('/vessel-ops/active-vessels')
def active_vessels():
    active_vessels = (
        db_session.query(Vessel)
        .join(Voyage)
        .join(Leg)
        .filter(Leg.eta >= datetime.now())
        .distinct()
        .all()
    )
    
    vessel_data = []
    for vessel in active_vessels:
        current_voyage = (
            db_session.query(Voyage)
            .join(Leg)
            .filter(Voyage.vessel_id == vessel.id)
            .filter(Leg.eta >= datetime.now())
            .first()
        )
        
        if current_voyage:
            current_leg = (
                db_session.query(Leg)
                .filter(Leg.voyage_id == current_voyage.id)
                .filter(Leg.eta >= datetime.now())
                .order_by(Leg.eta)
                .first()
            )
            
            next_leg = (
                db_session.query(Leg)
                .filter(Leg.voyage_id == current_voyage.id)
                .filter(Leg.eta >= datetime.now())
                .order_by(Leg.eta)
                .offset(1)
                .first()
            )
            
            vessel_data.append({
                'name': vessel.name,
                'current_location': current_leg.port.name if current_leg else 'Unknown',
                'next_port': next_leg.port.name if next_leg else 'N/A',
                'eta': next_leg.eta.strftime('%Y-%m-%d %H:%M') if next_leg else 'N/A',
                'status': 'In Transit' if next_leg else 'In Port'
            })
    
    return render_template('vessel_ops/active_vessels.html', vessels=vessel_data)

@vessel_ops.route('/vessel-ops/stats/total-vessels')
def total_vessels():
    count = db_session.query(func.count(Vessel.id)).scalar()
    return str(count)

@vessel_ops.route('/vessel-ops/stats/in-transit')
def vessels_in_transit():
    count = (
        db_session.query(func.count(distinct(Vessel.id)))
        .join(Voyage)
        .join(Leg)
        .filter(Leg.eta >= datetime.now())
        .scalar()
    )
    return str(count)

@vessel_ops.route('/vessel-ops/stats/in-port')
def vessels_in_port():
    total = db_session.query(func.count(Vessel.id)).scalar()
    in_transit = (
        db_session.query(func.count(distinct(Vessel.id)))
        .join(Voyage)
        .join(Leg)
        .filter(Leg.eta >= datetime.now())
        .scalar()
    )
    return str(total - in_transit)

@vessel_ops.route('/vessel-ops/upcoming-port-calls')
def upcoming_port_calls():
    upcoming_legs = (
        db_session.query(Leg)
        .join(Voyage)
        .join(Vessel)
        .filter(Leg.eta >= datetime.now())
        .order_by(Leg.eta)
        .limit(5)
        .all()
    )
    
    return render_template('vessel_ops/upcoming_port_calls.html', legs=upcoming_legs)

@vessel_ops.route('/vessel-ops/status-summary')
def status_summary():
    companies = (
        db_session.query(
            ShippingCompany,
            func.count(Vessel.id).label('vessel_count')
        )
        .join(Vessel)
        .group_by(ShippingCompany)
        .all()
    )
    
    return render_template('vessel_ops/status_summary.html', companies=companies)

@vessel_ops.route('/vessel-ops/manifests')
def manifests():
    manifests = (
        db_session.query(Manifest)
        .join(Voyage)
        .join(Vessel)
        .order_by(Manifest.date_of_receipt.desc())
        .all()
    )
    return render_template('vessel_ops/manifests.html', manifests=manifests)
