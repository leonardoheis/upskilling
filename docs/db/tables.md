# Database Tables (Draft)

This list is derived from the Team Management, Development Plans, Learning Paths,
Mentor Validation, and Path Creation screens shown in `docs/Upskills 01-16.pdf`.

## Core Tables

- `users`: People in the system.
- `roles`: Role catalog (admin, path creator, mentor, mentee),
  includes optional `max_active_paths` for limiting mentee assignments.
- `actions`: Atomic actions available in the system.
- `role_actions`: Join table mapping roles to allowed actions.
- `user_roles`: Join table linking users to roles (many-to-many, users can have multiple roles).
- `teams`: Manager-owned teams.
- `team_members`: Membership join table between teams and users.
- `careers`: Career tracks (e.g., Frontend Developer, UX/UI Designer).

## Path Definition

- `path_templates`: Canonical learning paths for a career (seniority encoded in path name).
- `path_template_steps`: Steps within a path (ordered parts of a path).
- `path_step_dependencies`: Dependency graph between steps in a path.

## Assignments & Progress

- `user_career_paths`: A user's assigned career track with start_date/end_date.
- `user_path_assignments`: Concrete path assignments tied to a user's career path.
- `user_step_progress`: Per-step status/progress for an assigned path.
  Includes planned and actual date tracking:
  - `planned_start_date` / `planned_end_date`: When the step is scheduled.
  - `actual_start_date` / `actual_end_date`: When the step actually started/finished.
- `log_entries`: Logbook entries for meetings, approvals, and project notes.

## Relationship Highlights

- One `user` has many `user_roles`; one `role` has many `user_roles` (many-to-many).
- One `team` has many `team_members`; each `team_member` is a `user`.
- One `career` has many `path_templates`.
- One `user` has many `user_career_paths`; each `user_career_path` has many
  `user_path_assignments`.
- `user_path_assignments` can be referenced from `log_entries` to capture
  approvals/rejections or other events tied to a specific path.
