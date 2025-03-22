# Active Context

This file tracks the project's current status, including recent changes, current goals, and open questions.
2025-03-22 14:56:10 - Log of updates made.

## Current Focus

* Troubleshooting an issue with the billing calculator where specific service selection returns zero amounts
* The issue appears when users select any services other than "All" in the frontend form
* When specific services are selected, the billing calculator fails to calculate costs correctly

## Recent Changes

* User has been investigating issues with the service selection in billing reports
* Frontend form has a dropdown to select specific services or "All" services
* Backend handling for service selection exists but may have logic issues

## Open Questions/Issues

* Why do billing calculations work correctly when "All" services are selected but not when specific services are chosen?
* Is the issue in the frontend parameter passing, API handling, or the calculator logic?
* How are rule groups being applied when services are filtered?
* Is there a difference in how service costs are calculated for specific vs. all services?