# Six-City × Six-Day Weather Demo

## Status

IMPLEMENTED — DEMO TOOL

This is a bounded Development Studio utility for fetching and flashing six-day forecast records for exactly six cities.

## Default cities

- Delhi
- London
- New York
- Tokyo
- Cairo
- Sydney

## Data

The adapter uses Open-Meteo's public geocoding and forecast endpoints. The tool normalizes daily date, high/low temperature, precipitation probability, and weather code.

## Boundary

This utility is not a KALP authority component. It does not authorize, schedule, invoke agents, manage credentials, or mutate registries. It is a small external-data demo that can later be connected through an explicitly governed Tool Gateway boundary.

## Verification status

Repository files and tests have been added. Runtime execution has not been claimed from GitHub because the current repository context does not provide arbitrary Python execution through the GitHub connector.
