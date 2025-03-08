from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import HealthRecord
from app.blueprints.health import health_bp
from app.blueprints.health.forms import HealthRecordForm
from datetime import datetime, timedelta
import json


@health_bp.route('/')
@login_required
def dashboard():
    return render_template('health/dashboard.html', title='Health Dashboard')


@health_bp.route('/records')
@login_required
def list_records():
    records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.date.desc()).all()
    return render_template('health/records.html', title='Health Records', records=records)


@health_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_record():
    form = HealthRecordForm()
    if form.validate_on_submit():
        record = HealthRecord(
            date=form.date.data,
            weight=form.weight.data,
            height=form.height.data,
            blood_pressure_systolic=form.blood_pressure_systolic.data,
            blood_pressure_diastolic=form.blood_pressure_diastolic.data,
            heart_rate=form.heart_rate.data,
            sleep_hours=form.sleep_hours.data,
            water_intake=form.water_intake.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(record)
        db.session.commit()
        flash('Health record added successfully!', 'success')
        return redirect(url_for('health.list_records'))

    # Default to today's date
    if request.method == 'GET':
        form.date.data = datetime.now().date()

    return render_template('health/record.html', title='New Health Record', form=form, is_update=False)


@health_bp.route('/<int:record_id>', methods=['GET'])
@login_required
def view_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)

    # Ensure the current user owns this record
    if record.user_id != current_user.id:
        abort(403)

    return render_template('health/view.html', title=f'Health Record for {record.date}', record=record)


@health_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)

    # Ensure the current user owns this record
    if record.user_id != current_user.id:
        abort(403)

    form = HealthRecordForm()

    if form.validate_on_submit():
        record.date = form.date.data
        record.weight = form.weight.data
        record.height = form.height.data
        record.blood_pressure_systolic = form.blood_pressure_systolic.data
        record.blood_pressure_diastolic = form.blood_pressure_diastolic.data
        record.heart_rate = form.heart_rate.data
        record.sleep_hours = form.sleep_hours.data
        record.water_intake = form.water_intake.data
        record.notes = form.notes.data
        db.session.commit()
        flash('Health record updated successfully!', 'success')
        return redirect(url_for('health.view_record', record_id=record.id))

    # Pre-fill the form with current data
    if request.method == 'GET':
        form.date.data = record.date
        form.weight.data = record.weight
        form.height.data = record.height
        form.blood_pressure_systolic.data = record.blood_pressure_systolic
        form.blood_pressure_diastolic.data = record.blood_pressure_diastolic
        form.heart_rate.data = record.heart_rate
        form.sleep_hours.data = record.sleep_hours
        form.water_intake.data = record.water_intake
        form.notes.data = record.notes

    return render_template('health/record.html', title='Edit Health Record', form=form, is_update=True)


@health_bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
def delete_record(record_id):
    record = HealthRecord.query.get_or_404(record_id)

    # Ensure the current user owns this record
    if record.user_id != current_user.id:
        abort(403)

    db.session.delete(record)
    db.session.commit()
    flash('Health record deleted successfully!', 'success')
    return redirect(url_for('health.list_records'))


@health_bp.route('/data')
@login_required
def get_health_data():
    # Get data for the last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    records = HealthRecord.query.filter(
        HealthRecord.user_id == current_user.id,
        HealthRecord.date >= start_date,
        HealthRecord.date <= end_date
    ).order_by(HealthRecord.date.asc()).all()

    data = {
        'dates': [record.date.strftime('%Y-%m-%d') for record in records],
        'weight': [record.weight for record in records],
        'heart_rate': [record.heart_rate for record in records],
        'sleep_hours': [record.sleep_hours for record in records],
        'water_intake': [record.water_intake for record in records],
        'blood_pressure': [
            {'systolic': record.blood_pressure_systolic, 'diastolic': record.blood_pressure_diastolic}
            for record in records
        ]
    }

    return jsonify(data)