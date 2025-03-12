# Personal Website

A secure, customizable personal dashboard and productivity platform built with Flask and Bootstrap.

## Features

### User Authentication
- Secure login and registration system with password hashing
- User profiles with customizable details
- "Remember me" functionality

### Dashboard Customization
- Personalized dashboard with drag-and-drop widget organization
- Resizable widgets for optimal viewing experience
- Enable/disable widgets based on your needs
- Add new widgets from a variety of data visualization options

### Health Tracking
- Track workouts, nutrition, and body metrics
- Monitor daily water intake
- View progress with interactive charts and reports
- Maintain a workout streak for motivation

### Task Management
- Create and manage todo items
- Assign tasks to users
- Track due dates and priorities
- Mark tasks as completed

### Calendar
- Schedule and organize events
- Invite other users to events
- Color-coded events for better visibility
- View events in daily, weekly, or monthly format

### Challenges
- Create and participate in challenges with other users
- Track progress toward challenge goals
- View leaderboards of participants

### Gaming Section
- Take a break with integrated games
- Track high scores and performance

## Technology Stack
- Flask web framework
- SQLAlchemy ORM
- Bootstrap 5 for responsive design
- JavaScript for interactivity
- Chart.js for data visualization
- SortableJS for drag-and-drop functionality

## Installation and Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables in `.env`
6. Initialize the database: `flask db upgrade`
7. Run the application: `flask run`