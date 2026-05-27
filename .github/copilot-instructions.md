# Project Instructions

## Context

This project is a local-first POS and business control system for a family pastry/snack shop.

Business context:

- sells pastries
- sugarcane juice
- snacks
- burgers
- pizza

Main goal:

Prevent financial leakage and understand business performance.

This software prioritizes:

1. reliability
2. simplicity
3. speed
4. few clicks
5. offline operation

## Architecture Principles

- Offline-first
- Local SQLite database
- Sync to cloud API when available
- Avoid overengineering
- Prefer pragmatic solutions
- Favor maintainability

## Technical Guidelines

- Python
- FastAPI for backend API
- SQLAlchemy
- SQLite locally
- Pydantic for DTOs
- Simple service layer
- Avoid premature abstractions
- Avoid enterprise complexity

## UX Principles

- Fast interactions
- Minimal clicks
- Large buttons for cashier usage
- Error-proof workflows
- Cashier must learn in minutes

## MVP Scope

Must include:

- cash register open/close
- sales registration
- payment methods
- expenses
- daily reports
- dashboard

Do NOT implement:

- advanced inventory
- fiscal emission
- loyalty
- CRM
- promotions
- analytics overkill

## Code Style

- readable over clever
- explicit naming
- avoid magic
- prefer simple functions
- keep modules cohesive