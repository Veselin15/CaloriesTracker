# 🥗 CaloriesTracker

[![Built with Django](https://img.shields.io/badge/Built%20with-Django-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Database PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

**CaloriesTracker** is a modern, full-stack web application designed to help users track their daily nutrition, set dietary goals, and visualize their progress. It leverages the **FatSecret Platform API** for accurate food data and uses **Chart.js** for interactive analytics.

🌐 **Live Demo:** [caloriestracker-yy3h.onrender.com](https://caloriestracker-yy3h.onrender.com)

---

## ✨ Features

- **👤 User Management:** Secure registration, login, and custom profile management (bio, gender, profile picture).
- **🍽️ Smart Food Tracking:** Search for food items using the FatSecret API to automatically fill nutrition data (Calories, Fat, Carbs, Protein).
- **📅 Meal Organization:** Log foods into specific meals (Breakfast, Lunch, Dinner, Snack) for any given date.
- **📊 Interactive Analytics:** Visualize your intake with dynamic charts for calorie consumption, macronutrient breakdown, and weight progress over time.
- **🎯 Goal Setting:** Set and update personalized daily goals for calories, macros, and target weight.
- **⚖️ Weight Logging:** Track your weight history to monitor your physical progress.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.12, Django 5.2
* **Database:** PostgreSQL 15 (via Docker)
* **API Integration:** FatSecret Platform API (OAuth 2.0)
* **Frontend:** HTML5, Bootstrap 5, Chart.js
* **Containerization:** Docker, Docker Compose

---

## 🚀 Getting Started

### Prerequisites

* **Docker Desktop** (Recommended)
* *OR* Python 3.11+ and PostgreSQL installed locally.
* **FatSecret API Credentials:** You must obtain a Client ID and Client Secret from the [FatSecret Platform](https://platform.fatsecret.com/).

### 🔑 Environment Variables

Create a `.env` file in the root directory (next to `manage.py`) with the following settings:

```env
# Django Settings
SECRET_KEY=your_django_secret_key
DEBUG=1

# Database Configuration
DB_NAME=calories_tracker
DB_USER=postgres
DB_PASS=postgres
DB_HOST=db  # Use 'localhost' if running without Docker
POSTGRES_DB=calories_tracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# FatSecret API Credentials
FATSECRET_CLIENT_ID=your_fatsecret_client_id
FATSECRET_CLIENT_SECRET=your_fatsecret_client_secret
