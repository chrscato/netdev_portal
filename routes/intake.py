from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import db
from models.provider import Provider
from models.contact import Contact
import uuid
import os
from utils.generate_contract import generate_contract

intake_bp = Blueprint("intake", __name__, url_prefix="/providers")


@intake_bp.route("/<provider_id>/generate_contract", methods=["POST"])
def generate_contract_route(provider_id):
    try:
        provider = Provider.query.get(provider_id)
        if not provider:
            flash("Provider not found")
            return redirect(url_for("provider.list_providers"))

        # Get WCFS percentages if using WCFS method
        wcfs_percentages = None
        if provider.rate_type == 'wcfs':
            wcfs_percentages = provider.wcfs_percentages_dict

        docx_path, pdf_path = generate_contract(
            provider_id,
            method=provider.rate_type,
            wcfs_percentages=wcfs_percentages
        )
        
        # Check if files were generated
        if os.path.exists(docx_path):
            flash(f"Contract generated successfully! DOCX file available.")
        else:
            flash("Error: DOCX file was not generated.")
            
        if os.path.exists(pdf_path):
            flash(f"PDF version available.")
        else:
            flash("Note: PDF conversion failed. Only DOCX version is available.")
            
    except Exception as e:
        flash(f"Error generating contract: {e}")
    return redirect(url_for("provider.list_providers"))

@intake_bp.route("/<provider_id>/download/<file_type>")
def download_contract(provider_id, file_type):
    try:
        if file_type not in ['docx', 'pdf']:
            flash("Invalid file type")
            return redirect(url_for("provider.list_providers"))
            
        file_path = os.path.join("contracts", f"contract_{provider_id}.{file_type}")
        if not os.path.exists(file_path):
            flash(f"Contract file not found")
            return redirect(url_for("provider.list_providers"))
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"contract_{provider_id}.{file_type}"
        )
    except Exception as e:
        flash(f"Error downloading file: {e}")
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