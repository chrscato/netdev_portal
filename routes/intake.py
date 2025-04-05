from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.provider import Provider
from models.contact import Contact
import uuid
from utils.generate_contract import generate_contract

intake_bp = Blueprint("intake", __name__, url_prefix="/providers")


@intake_bp.route("/<provider_id>/generate_contract", methods=["POST"])
def generate_contract_route(provider_id):
    try:
        docx_path, pdf_path = generate_contract(provider_id)
        flash(f"Contract generated successfully.")
    except Exception as e:
        flash(f"Error generating contract: {e}")
    return redirect(url_for("provider.list_providers"))

@intake_bp.route("/intake", methods=["GET", "POST"])
def provider_intake():
    if request.method == "POST":
        provider = Provider(
            id=str(uuid.uuid4()),
            name=request.form["name"],
            dba_name=request.form["dba_name"],
            address=request.form["address"],
            provider_type=request.form["provider_type"],
            states_in_contract=request.form["states"],
            rate_type=request.form["rate_type"],
            wcfs_percentage=request.form.get("wcfs_percentage") or None
        )
        db.session.add(provider)
        db.session.commit()

        # Handle multiple contacts
        contact_names = request.form.getlist("contact_name[]")
        contact_phones = request.form.getlist("contact_phone[]")
        contact_emails = request.form.getlist("contact_email[]")

        for name, phone, email in zip(contact_names, contact_phones, contact_emails):
            if name:  # skip empty rows
                contact = Contact(
                    id=str(uuid.uuid4()),
                    provider_id=provider.id,
                    name=name,
                    phone=phone,
                    email=email
                )
                db.session.add(contact)
        db.session.commit()

        flash("Provider and contacts saved!")
        return redirect(url_for("provider.list_providers"))

    return render_template("providers/intake.html") 