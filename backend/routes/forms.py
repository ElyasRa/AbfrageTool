"""
API routes for form endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from auth import get_current_user, User

router = APIRouter()


class FormData(BaseModel):
    """Generic form data model"""
    form_type: str
    data: Dict[str, Any]


@router.post("/api/forms/submit")
async def submit_form(form_data: FormData, current_user: User = Depends(get_current_user)):
    """
    Submit form data (for future processing/storage)
    """
    return {
        "status": "success",
        "message": "Form data received",
        "form_type": form_data.form_type,
        "user": current_user.username
    }


@router.get("/api/forms/types")
async def get_form_types(current_user: User = Depends(get_current_user)):
    """
    Get available form types
    """
    forms = [
        {
            "id": "panne-unfall",
            "name": "Abklärung Panne/Unfall",
            "icon": "🔧",
            "color": "#D32F2F",
            "description": "Umfassende Abklärung von Pannen und Unfällen"
        },
        {
            "id": "oelspur",
            "name": "Annahme Ölspur",
            "icon": "💧",
            "color": "#1976D2",
            "description": "Erfassung von Ölspuren und Umwelteinsätzen"
        },
        {
            "id": "mobi",
            "name": "Annahme Mobi",
            "icon": "📱",
            "color": "#FFC107",
            "description": "Bearbeitung von Mobilitätsgarantie-Fällen"
        },
        {
            "id": "kilian",
            "name": "Annahme Kilian",
            "icon": "🚛",
            "color": "#388E3C",
            "description": "Aufträge für die Polizei, GDV und Bus/LKW"
        },
        {
            "id": "rudolph",
            "name": "Annahme Rudolph",
            "icon": "👮",
            "color": "#7B1FA2",
            "description": "Umsetzungen und Sicherstellungen für FUBZ/BVG"
        },
        {
            "id": "wehner",
            "name": "Annahme Wehner Motors",
            "icon": "🛠️",
            "color": "#F57C00",
            "description": "PKW, Polizei, LKW und Ölspur Aufträge"
        },
        {
            "id": "falschparker",
            "name": "Falschparker | Privat",
            "icon": "🅿️",
            "color": "#009688",
            "description": "Private Falschparker-Meldungen"
        },
        {
            "id": "unterhaslberger",
            "name": "Annahme Unterhaslberger",
            "icon": "🏗️",
            "color": "#009688",
            "description": "Pannen, Unfälle und Sicherstellungen"
        },
        {
            "id": "safar-bhg",
            "name": "Report Safar & BHG",
            "icon": "📊",
            "color": "#D32F2F",
            "description": "Tägliche Reports für Safar und Bad Homburg"
        }
    ]
    return {"forms": forms}
