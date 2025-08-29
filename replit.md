# Overview

This is a Telegram bot application for a star-based gaming platform where users can purchase stars, play slot-style games, and withdraw winnings. The system includes a comprehensive admin panel for monitoring and managing the platform.

The bot allows users to:
- Purchase star packages using Telegram Stars payment system
- Play gambling games with configurable return rates
- Request withdrawals that require admin approval
- View their statistics and transaction history

The admin panel provides real-time analytics, user management, and withdrawal approval workflows.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: FastAPI for the admin panel web interface and aiogram for Telegram bot interactions
- **Database**: PostgreSQL with SQLAlchemy ORM using async patterns
- **Concurrency**: Asyncio-based architecture for handling multiple concurrent users
- **Process Management**: Multiprocessing to run bot and admin panel simultaneously

## Database Design
- **Users Table**: Stores user profiles, balances, and lifetime statistics
- **Transactions Table**: Records all financial activities (purchases, wins, withdrawals)
- **Withdrawals Table**: Manages withdrawal requests with approval workflow
- **SpinResults Table**: Tracks individual game outcomes for auditing

## Game Logic
- **Return Rate**: Configurable 30% win probability with 1.5x to 5x multipliers
- **Spin Costs**: Multiple bet levels (10, 25, 50 stars) for different risk profiles
- **Minimum Withdrawal**: 150 stars threshold to prevent micro-transactions

## Authentication & Authorization
- **Admin Access**: Environment variable-based admin user list
- **User Verification**: Telegram user ID-based authentication
- **Session Management**: SQLAlchemy async sessions with proper cleanup

## Payment Integration
- **Telegram Stars**: Native Telegram payment system for star purchases
- **Transaction Tracking**: Complete audit trail for all financial operations
- **Withdrawal Approval**: Manual admin review process for payouts

# External Dependencies

## Core Services
- **Telegram Bot API**: Primary user interface through aiogram library
- **PostgreSQL Database**: Persistent data storage with asyncpg driver
- **Telegram Stars Payment**: Official Telegram payment processor

## Infrastructure Components
- **Uvicorn**: ASGI server for the FastAPI admin panel
- **SQLAlchemy**: Database ORM with async support
- **Jinja2**: Template engine for admin panel HTML rendering
- **Bootstrap**: Frontend CSS framework for responsive admin interface

## Configuration Management
- **Environment Variables**: Bot tokens, database URLs, admin IDs, and payment credentials
- **Star Packages**: Configurable pricing tiers for different purchase amounts
- **Game Parameters**: Adjustable return rates and minimum withdrawal thresholds