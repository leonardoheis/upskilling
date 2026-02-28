-- Relational schema for UpSkills demo data

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  bio TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
  role_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  max_active_paths INTEGER CHECK (max_active_paths IS NULL OR max_active_paths >= 0)
);

CREATE TABLE actions (
  action_id INTEGER PRIMARY KEY,
  action_key TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL
);

CREATE TABLE role_actions (
  role_id INTEGER NOT NULL REFERENCES roles(role_id),
  action_id INTEGER NOT NULL REFERENCES actions(action_id),
  PRIMARY KEY (role_id, action_id)
);

CREATE TABLE user_roles (
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  role_id INTEGER NOT NULL REFERENCES roles(role_id),
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE teams (
  team_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  manager_user_id INTEGER NOT NULL REFERENCES users(user_id)
);

CREATE TABLE team_members (
  team_id INTEGER NOT NULL REFERENCES teams(team_id),
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  PRIMARY KEY (team_id, user_id)
);

CREATE TABLE careers (
  career_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  specialization TEXT
);

CREATE TABLE path_templates (
  path_template_id INTEGER PRIMARY KEY,
  career_id INTEGER NOT NULL REFERENCES careers(career_id),
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  duration_hours INTEGER NOT NULL,
  default_start_offset_days INTEGER,
  default_deadline_offset_days INTEGER
);

CREATE TABLE path_template_steps (
  step_id INTEGER PRIMARY KEY,
  path_template_id INTEGER NOT NULL REFERENCES path_templates(path_template_id),
  step_order INTEGER NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  duration_hours INTEGER,
  course_link TEXT,
  UNIQUE (path_template_id, step_order)
);

CREATE TABLE path_step_dependencies (
  step_id INTEGER NOT NULL REFERENCES path_template_steps(step_id),
  depends_on_step_id INTEGER NOT NULL REFERENCES path_template_steps(step_id),
  PRIMARY KEY (step_id, depends_on_step_id)
);

CREATE TABLE user_career_paths (
  user_career_path_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  career_id INTEGER NOT NULL REFERENCES careers(career_id),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  overall_progress_percent INTEGER NOT NULL
    CHECK (overall_progress_percent BETWEEN 0 AND 100)
);

CREATE TABLE user_path_assignments (
  user_path_assignment_id INTEGER PRIMARY KEY,
  user_career_path_id INTEGER NOT NULL
    REFERENCES user_career_paths(user_career_path_id),
  path_template_id INTEGER NOT NULL REFERENCES path_templates(path_template_id),
  start_date DATE NOT NULL,
  deadline DATE NOT NULL,
  status TEXT NOT NULL
    CHECK (status IN ('Pending', 'In Progress', 'Completed')),
  progress_percent INTEGER NOT NULL CHECK (progress_percent BETWEEN 0 AND 100),
  mentor_validation_status TEXT NOT NULL
    CHECK (mentor_validation_status IN ('Pending', 'Approved', 'Rejected'))
);

CREATE TABLE user_step_progress (
  user_step_progress_id INTEGER PRIMARY KEY,
  user_path_assignment_id INTEGER NOT NULL
    REFERENCES user_path_assignments(user_path_assignment_id),
  step_id INTEGER NOT NULL REFERENCES path_template_steps(step_id),
  status TEXT NOT NULL
    CHECK (status IN ('Pending', 'In Progress', 'Completed')),
  progress_percent INTEGER NOT NULL CHECK (progress_percent BETWEEN 0 AND 100),
  planned_start_date DATE,
  planned_end_date DATE,
  actual_start_date DATE,
  actual_end_date DATE,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_path_assignment_id, step_id)
);

CREATE TABLE log_entries (
  log_entry_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(user_id),
  user_career_path_id INTEGER NOT NULL
    REFERENCES user_career_paths(user_career_path_id),
  entry_type TEXT NOT NULL
    CHECK (entry_type IN (
      'Meeting/Conversation',
      'Path Approved',
      'Path Rejected',
      'Final Project',
      'General'
    )),
  entry_date DATE NOT NULL,
  notes TEXT NOT NULL,
  related_user_path_assignment_id INTEGER
    REFERENCES user_path_assignments(user_path_assignment_id)
);

