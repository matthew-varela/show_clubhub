# ClubHub 🌐

> The organized, always-current hub for finding and managing campus clubs.

## Overview
ClubHub lets students browse clubs by interest, see who’s in charge, and never miss an event.  
A single Django back end serves both the public directory and authenticated member dashboards.

## Core Features
| Area              | What it does                                                      |
|-------------------|-------------------------------------------------------------------|
| 🔍 Discover       | Tag-based search & fuzzy matching across all registered clubs     |
| 👤 Profiles       | Show your memberships and upcoming events in one place            |
| 🏷️ Club pages    | Officer roster, contact links, affiliations, photo banner         |
| 📅 Events         | Officers post events → auto-publish to members’ calendars (iCal)  |
| 🚀 Deployment     | One-click Heroku pipeline, **MySQL** database, S3 media storage   |

## Tech Stack
- **Backend:** Django 5, Django REST Framework  
- **Database:** **MySQL** (Heroku ClearDB)  
- **Styling:** Tailwind CSS + HTMX (progressive enhancement)  
- **CI/CD:** GitHub Actions → Heroku review apps