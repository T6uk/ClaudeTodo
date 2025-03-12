# app/utils/insights.py
"""
Utilities for generating intelligent insights from user health data
"""
from datetime import datetime, timedelta
from collections import Counter
import numpy as np
from sqlalchemy import func

from app import db
from app.models.workout import Workout
from app.models.meal import Meal
from app.models.body_metrics import BodyMetrics
from app.models.water_intake import WaterIntake
from app.models.exercise import Exercise


def get_workout_recommendations(user_id):
    """
    Generate personalized workout recommendations based on user's workout history

    Args:
        user_id (int): User ID to generate recommendations for

    Returns:
        dict: Dictionary containing personalized recommendations
    """
    # Get user's workout history (last 90 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)

    workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.date >= start_date
    ).all()

    if not workouts:
        return {
            'message': "Not enough workout history to generate personalized recommendations.",
            'suggestions': [
                "Try starting with 2-3 workouts per week",
                "Mix cardio and strength training for balanced fitness",
                "Start with 20-30 minute sessions and gradually increase"
            ]
        }

    # Analyze workout frequency
    workout_dates = [w.date.date() for w in workouts]
    workout_counts = Counter(workout_dates)

    # Get workout types distribution
    workout_types = Counter([w.workout_type for w in workouts])
    most_common_type = workout_types.most_common(1)[0][0] if workout_types else None

    # Calculate average workout duration
    avg_duration = sum([w.duration for w in workouts]) / len(workouts) if workouts else 0

    # Calculate weekly frequency
    weeks = (end_date.date() - start_date.date()).days // 7
    weekly_frequency = len(workouts) / weeks if weeks > 0 else 0

    # Generate recommendations based on analysis
    recommendations = {
        'insights': [],
        'suggestions': []
    }

    # Frequency insights
    if weekly_frequency < 1:
        recommendations['insights'].append(
            "Your workout frequency is lower than recommended (less than once per week).")
        recommendations['suggestions'].append("Try to increase to at least 2-3 workouts per week for better results.")
    elif weekly_frequency < 3:
        recommendations['insights'].append(f"You're averaging {weekly_frequency:.1f} workouts per week.")
        recommendations['suggestions'].append("Consider adding 1-2 more workouts per week to reach optimal frequency.")
    else:
        recommendations['insights'].append(f"Great job! You're averaging {weekly_frequency:.1f} workouts per week.")

    # Duration insights
    if avg_duration < 20:
        recommendations['insights'].append(f"Your average workout duration is {avg_duration:.1f} minutes.")
        recommendations['suggestions'].append("Try to extend your workouts to at least 30 minutes for better results.")
    elif avg_duration < 30:
        recommendations['insights'].append(f"Your average workout duration is {avg_duration:.1f} minutes.")
        recommendations['suggestions'].append(
            "Consider increasing workout duration to 40-45 minutes for optimal benefits.")
    else:
        recommendations['insights'].append(f"Your average workout duration of {avg_duration:.1f} minutes is excellent!")

    # Workout variety insights
    if len(workout_types) == 1:
        recommendations['insights'].append(f"You're primarily doing {most_common_type} workouts.")
        if most_common_type == 'cardio':
            recommendations['suggestions'].append(
                "Consider adding strength training 2-3 times per week to build muscle.")
        elif most_common_type == 'strength':
            recommendations['suggestions'].append("Consider adding cardio 2-3 times per week for heart health.")
        else:
            recommendations['suggestions'].append("Try to diversify your workout routine for balanced fitness.")

    # Check for missing workout types
    all_types = {'cardio', 'strength', 'flexibility', 'hiit', 'yoga'}
    missing_types = all_types - set(workout_types.keys())

    if missing_types:
        if 'cardio' in missing_types and 'strength' in missing_types:
            recommendations['suggestions'].append(
                "Your routine would benefit from adding both cardio and strength training.")
        elif 'cardio' in missing_types:
            recommendations['suggestions'].append("Consider adding cardio workouts for heart health and endurance.")
        elif 'strength' in missing_types:
            recommendations['suggestions'].append(
                "Adding strength training would help build muscle and boost metabolism.")

        if 'flexibility' in missing_types and 'yoga' in missing_types:
            recommendations['suggestions'].append("Consider adding yoga or stretching sessions to improve flexibility.")

    # Recommend next workout
    if most_common_type == 'cardio':
        recommendations['next_workout'] = {
            'type': 'strength',
            'title': 'Full Body Strength Training',
            'duration': 45
        }
    else:
        recommendations['next_workout'] = {
            'type': 'cardio',
            'title': 'Interval Cardio Session',
            'duration': 30
        }

    return recommendations


def analyze_trends(user_id):
    """
    Analyze trends in user's health data

    Args:
        user_id (int): User ID to analyze

    Returns:
        dict: Dictionary containing trend analysis
    """
    # Get data from the last 90 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=90)

    # Get weight trend data
    metrics = BodyMetrics.query.filter(
        BodyMetrics.user_id == user_id,
        BodyMetrics.date >= start_date,
        BodyMetrics.weight.isnot(None)
    ).order_by(BodyMetrics.date).all()

    # Get workout data
    workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.date >= start_date
    ).order_by(Workout.date).all()

    # Get meal data
    meals = Meal.query.filter(
        Meal.user_id == user_id,
        Meal.meal_time >= start_date
    ).order_by(Meal.meal_time).all()

    trends = {
        'weight': {},
        'workouts': {},
        'nutrition': {},
        'correlations': []
    }

    # Analyze weight trend
    if len(metrics) >= 2:
        weights = [m.weight for m in metrics if m.weight is not None]
        dates = [m.date for m in metrics if m.weight is not None]

        if weights:
            first_weight = weights[0]
            last_weight = weights[-1]
            weight_change = last_weight - first_weight

            # Calculate trend using linear regression
            if len(weights) >= 3:
                x = np.array(range(len(weights)))
                y = np.array(weights)
                slope, _ = np.polyfit(x, y, 1)

                trends['weight'] = {
                    'direction': 'increasing' if slope > 0.01 else ('decreasing' if slope < -0.01 else 'stable'),
                    'change': weight_change,
                    'percent_change': (weight_change / first_weight) * 100 if first_weight else 0,
                    'start_weight': first_weight,
                    'current_weight': last_weight,
                    'rate': abs(slope) * 7  # weekly change
                }
            else:
                trends['weight'] = {
                    'direction': 'increasing' if weight_change > 0 else (
                        'decreasing' if weight_change < 0 else 'stable'),
                    'change': weight_change,
                    'percent_change': (weight_change / first_weight) * 100 if first_weight else 0,
                    'start_weight': first_weight,
                    'current_weight': last_weight
                }

    # Analyze workout trends
    if workouts:
        # Group workouts by week
        workout_weeks = {}
        start_week = (start_date - timedelta(days=start_date.weekday())).date()
        for workout in workouts:
            week_start = (workout.date - timedelta(days=workout.date.weekday())).date()
            week_key = (week_start - start_week).days // 7

            if week_key not in workout_weeks:
                workout_weeks[week_key] = []

            workout_weeks[week_key].append(workout)

        # Calculate weekly averages
        weekly_counts = []
        weekly_durations = []

        for week, week_workouts in sorted(workout_weeks.items()):
            weekly_counts.append(len(week_workouts))
            weekly_durations.append(sum(w.duration for w in week_workouts))

        if weekly_counts:
            # Calculate trends using linear regression
            x = np.array(range(len(weekly_counts)))

            if len(weekly_counts) >= 2:
                y_count = np.array(weekly_counts)
                count_slope, _ = np.polyfit(x, y_count, 1)

                y_duration = np.array(weekly_durations)
                duration_slope, _ = np.polyfit(x, y_duration, 1)

                trends['workouts'] = {
                    'frequency_trend': 'increasing' if count_slope > 0.1 else (
                        'decreasing' if count_slope < -0.1 else 'stable'),
                    'duration_trend': 'increasing' if duration_slope > 1 else (
                        'decreasing' if duration_slope < -1 else 'stable'),
                    'avg_weekly_workouts': sum(weekly_counts) / len(weekly_counts),
                    'avg_weekly_minutes': sum(weekly_durations) / len(weekly_durations)
                }

    # Analyze nutrition trends
    if meals:
        # Group meals by day
        daily_calories = {}
        daily_protein = {}

        for meal in meals:
            day = meal.meal_time.date()

            if day not in daily_calories:
                daily_calories[day] = 0
                daily_protein[day] = 0

            if meal.calories is not None:
                daily_calories[day] += meal.calories

            if meal.protein is not None:
                daily_protein[day] += meal.protein

        if daily_calories:
            avg_daily_calories = sum(daily_calories.values()) / len(daily_calories)

            # Calculate protein consistency
            protein_values = list(daily_protein.values())
            protein_std = np.std(protein_values) if protein_values else 0

            trends['nutrition'] = {
                'avg_daily_calories': avg_daily_calories,
                'avg_daily_protein': sum(daily_protein.values()) / len(daily_protein) if daily_protein else 0,
                'protein_consistency': 'consistent' if protein_std < 15 else 'variable',
                'calorie_logging_consistency': len(daily_calories) / (end_date - start_date).days
            }

    # Look for correlations
    if workouts and metrics and len(metrics) >= 3:
        # Check for correlation between workout frequency and weight changes
        metrics_by_date = {m.date.date(): m for m in metrics if m.weight is not None}
        workouts_by_date = {}

        for workout in workouts:
            day = workout.date.date()
            if day not in workouts_by_date:
                workouts_by_date[day] = []
            workouts_by_date[day].append(workout)

        # Check weeks with consistent workouts vs weight
        has_correlation = False

        if trends.get('weight', {}).get('direction') == 'decreasing' and trends.get('workouts', {}).get(
                'frequency_trend') == 'increasing':
            trends['correlations'].append("Your increased workout frequency appears to be helping with weight loss.")
            has_correlation = True

        if not has_correlation and trends.get('weight', {}).get('direction') == 'decreasing' and trends.get('nutrition',
                                                                                                            {}).get(
                'avg_daily_calories', 0) < 2000:
            trends['correlations'].append("Your calorie control appears to be contributing to your weight loss.")
            has_correlation = True

        if not has_correlation and trends.get('weight', {}).get('direction') == 'increasing' and trends.get('workouts',
                                                                                                            {}).get(
                'frequency_trend') == 'decreasing':
            trends['correlations'].append("Your decrease in workout frequency may be contributing to weight gain.")

    return trends


def generate_user_insights(user_id):
    """
    Generate comprehensive health insights for a user

    Args:
        user_id (int): User ID to generate insights for

    Returns:
        dict: Dictionary containing all insights and recommendations
    """
    recommendations = get_workout_recommendations(user_id)
    trends = analyze_trends(user_id)

    insights = {
        'recommendations': recommendations,
        'trends': trends,
        'summary': []
    }

    # Generate summary insights
    if trends.get('weight', {}).get('direction') == 'decreasing' and trends.get('weight', {}).get('change', 0) < -2:
        # Use abs() explicitly here
        change = abs(trends['weight']['change'])
        insights['summary'].append(f"You've lost {change:.1f} kg over the past 90 days. Great progress!")

    if recommendations.get('insights'):
        insights['summary'].extend(recommendations['insights'][:2])

    if trends.get('correlations'):
        insights['summary'].extend(trends['correlations'])

    if 'next_workout' in recommendations:
        next_type = recommendations['next_workout']['type'].capitalize()
        next_title = recommendations['next_workout']['title']
        insights['summary'].append(f"Recommended next workout: {next_title} ({next_type})")

    return insights