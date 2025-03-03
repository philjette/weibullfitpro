import streamlit as st
from datetime import datetime
from utils.database import WeibullCurve, get_db

def initialize_storage():
    """Initialize database connection if needed."""
    pass  # Database is initialized when imported

def save_curve(name, description, shape, scale, method, user_id):
    """Save a curve to the database."""
    if not name:
        return False, "Please provide a name for the curve"

    if not user_id:
        return False, "Please log in to save curves"

    try:
        db = next(get_db())
        curve = WeibullCurve(
            name=name,
            description=description,
            shape=shape,
            scale=scale,
            method=method,
            user_id=user_id
        )
        db.add(curve)
        db.commit()
        return True, "Curve saved successfully"
    except Exception as e:
        return False, f"Error saving curve: {str(e)}"

def delete_curve(curve_name, user_id):
    """Delete a curve from the database."""
    if not user_id:
        return False, "Please log in to delete curves"

    try:
        db = next(get_db())
        curve = db.query(WeibullCurve)\
            .filter(WeibullCurve.name == curve_name)\
            .filter(WeibullCurve.user_id == user_id)\
            .first()

        if not curve:
            return False, "Curve not found"

        db.delete(curve)
        db.commit()
        return True, "Curve deleted successfully"
    except Exception as e:
        db.rollback()
        return False, f"Error deleting curve: {str(e)}"

def get_saved_curves(user_id):
    """Retrieve all saved curves for a specific user from the database."""
    if not user_id:
        return []

    db = next(get_db())
    curves = db.query(WeibullCurve)\
        .filter(WeibullCurve.user_id == user_id)\
        .order_by(WeibullCurve.timestamp.desc())\
        .all()

    return [
        {
            'name': curve.name,
            'description': curve.description,
            'shape': curve.shape,
            'scale': curve.scale,
            'method': curve.method,
            'timestamp': curve.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for curve in curves
    ]