# KBO Baseball Android App

Jetpack Compose based Android app starter for checking:

- KBO game schedules
- Team standings
- Player stats

## Current status

- Official KBO pages are used as the primary data source
- If live parsing fails, the app falls back to local sample data
- Three tabs: schedules, standings, players
- Loading state and manual refresh button included
- Player search included
- Team detail view included from standings screen

## Next recommended steps

1. Open this folder in Android Studio.
2. Let Android Studio create the Gradle wrapper files if prompted.
3. Sync Gradle and run on an emulator or Android device.
4. Add richer player detail screens.
5. Replace HTML scraping with a stable JSON API if you secure one later.
