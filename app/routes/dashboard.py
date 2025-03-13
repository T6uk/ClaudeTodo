# app/routes/dashboard.py
"""
Dashboard routes for dashboard customization
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from sqlalchemy import func

from app import db
from app.models.dashboard_widget import DashboardWidget

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/customize")
@login_required
def customize():
    """Dashboard customization page"""
    # Get current user's widgets
    widgets = DashboardWidget.query.filter_by(user_id=current_user.id).order_by(DashboardWidget.position).all()

    # If no widgets exist yet, create defaults
    if not widgets:
        default_widgets = [
            {"type": "workout_stats", "position": 0, "size": "medium"},
            {"type": "water_tracker", "position": 1, "size": "medium"},
            {"type": "workout_streak", "position": 2, "size": "small"},
            {"type": "body_metrics", "position": 3, "size": "medium"},
            {"type": "nutrition_stats", "position": 4, "size": "medium"},
            {"type": "recent_workouts", "position": 5, "size": "large"},
            {"type": "recent_meals", "position": 6, "size": "large"}
        ]

        for widget in default_widgets:
            new_widget = DashboardWidget(
                user_id=current_user.id,
                widget_type=widget["type"],
                position=widget["position"],
                size=widget["size"]
            )
            db.session.add(new_widget)

        db.session.commit()

        # Reload widgets
        widgets = DashboardWidget.query.filter_by(user_id=current_user.id).order_by(DashboardWidget.position).all()

    # Get available widget types for adding new widgets
    available_widget_types = [
        {"id": "workout_stats", "name": "Workout Statistics", "description": "Summary of your workout data"},
        {"id": "water_tracker", "name": "Water Tracker", "description": "Track your daily water intake"},
        {"id": "workout_streak", "name": "Workout Streak", "description": "Track your current workout streak"},
        {"id": "body_metrics", "name": "Body Metrics", "description": "Display your latest body measurements"},
        {"id": "nutrition_stats", "name": "Nutrition Stats", "description": "Summary of your nutrition data"},
        {"id": "recent_workouts", "name": "Recent Workouts", "description": "List of your most recent workouts"},
        {"id": "recent_meals", "name": "Recent Meals", "description": "List of your most recent meals"},
        {"id": "weight_chart", "name": "Weight Chart", "description": "Chart of your weight progress"},
        {"id": "workout_calendar", "name": "Workout Calendar", "description": "Calendar view of your workouts"},
        {"id": "macronutrients", "name": "Macronutrients", "description": "Breakdown of your macronutrient intake"},
        {"id": "calories_chart", "name": "Calories Chart", "description": "Chart of your calorie intake"},
        {"id": "goal_progress", "name": "Goal Progress", "description": "Progress towards your health goals"},
        {"id": "recent_diary", "name": "Recent Diary Entries", "description": "Your latest diary entries"}

    ]

    return render_template("dashboard/customize.html",
                           title="Customize Dashboard",
                           widgets=widgets,
                           available_widget_types=available_widget_types)


@dashboard_bp.route("/dashboard/widgets", methods=["GET"])
@login_required
def get_widgets():
    """Get user's dashboard widgets as JSON"""
    widgets = DashboardWidget.query.filter_by(user_id=current_user.id).order_by(DashboardWidget.position).all()
    return jsonify([widget.to_dict() for widget in widgets])


@dashboard_bp.route("/dashboard/widgets/update", methods=["POST"])
@login_required
def update_widgets():
    """Update widget positions from drag-and-drop"""
    try:
        # Get the submitted widget data
        widget_data = request.json

        if not widget_data or not isinstance(widget_data, list):
            return jsonify({"success": False, "message": "Invalid data format"}), 400

        # Process each widget update
        for item in widget_data:
            widget_id = item.get('id')
            new_position = item.get('position')

            if widget_id is None or new_position is None:
                continue

            # Find the widget and update its position
            widget = DashboardWidget.query.filter_by(id=widget_id, user_id=current_user.id).first()
            if widget:
                widget.position = new_position

        db.session.commit()
        return jsonify({"success": True, "message": "Dashboard layout updated successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error updating layout: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/widgets/<int:widget_id>/toggle", methods=["POST"])
@login_required
def toggle_widget(widget_id):
    """Toggle widget enabled status"""
    widget = DashboardWidget.query.filter_by(id=widget_id, user_id=current_user.id).first_or_404()

    try:
        widget.enabled = not widget.enabled
        db.session.commit()
        return jsonify({"success": True, "enabled": widget.enabled})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error toggling widget: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/widgets/<int:widget_id>/resize", methods=["POST"])
@login_required
def resize_widget(widget_id):
    """Change widget size"""
    widget = DashboardWidget.query.filter_by(id=widget_id, user_id=current_user.id).first_or_404()

    try:
        new_size = request.json.get('size')
        if new_size not in ['small', 'medium', 'large']:
            return jsonify({"success": False, "message": "Invalid size"}), 400

        widget.size = new_size
        db.session.commit()
        return jsonify({"success": True, "size": widget.size})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error resizing widget: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/widgets/create", methods=["POST"])
@login_required
def create_widget():
    """Add a new widget to dashboard"""
    try:
        widget_type = request.json.get('widget_type')
        if not widget_type:
            return jsonify({"success": False, "message": "Widget type is required"}), 400

        # Get the highest position value
        max_position = db.session.query(func.max(DashboardWidget.position)).filter_by(
            user_id=current_user.id).scalar() or -1
        new_position = max_position + 1

        # Create the new widget
        widget = DashboardWidget(
            user_id=current_user.id,
            widget_type=widget_type,
            position=new_position,
            size='medium'  # Default size
        )

        db.session.add(widget)
        db.session.commit()

        return jsonify({"success": True, "widget": widget.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error creating widget: {str(e)}"}), 500


@dashboard_bp.route("/dashboard/widgets/<int:widget_id>/delete", methods=["POST"])
@login_required
def delete_widget(widget_id):
    """Delete a widget from dashboard"""
    widget = DashboardWidget.query.filter_by(id=widget_id, user_id=current_user.id).first_or_404()

    try:
        db.session.delete(widget)

        # Reorder remaining widgets to close gaps
        remaining_widgets = DashboardWidget.query.filter_by(user_id=current_user.id).order_by(
            DashboardWidget.position).all()
        for i, w in enumerate(remaining_widgets):
            w.position = i

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error deleting widget: {str(e)}"}), 500