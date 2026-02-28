# UpSkills

A career development and upskilling platform that enables organizations to manage learning paths, track employee progress, and facilitate mentor-mentee relationships.

## Overview

UpSkills helps organizations:

- **Define Career Paths**: Create structured learning journeys with courses, steps, and dependencies
- **Assign & Track Progress**: Mentors assign paths to mentees and monitor completion
- **Validate Learning**: Mentors approve/reject completed steps and provide feedback via logbook entries
- **Manage Teams**: Organize users into teams with managers overseeing progress

## Roles

| Role | Responsibilities |
|------|------------------|
| **Admin** | Full system access - manage users, roles, careers, paths, and all settings |
| **Path Creator** | Create and edit career paths, define steps and dependencies, manage content |
| **Mentor** | Assign paths to mentees, validate progress, approve/reject steps, add logbook feedback |
| **Mentee** | View assigned paths, track progress, mark steps complete (pending validation) |

## Tech Stack

- **Frontend**: React
- **Backend**: .NET 10
- **Database**: Relational (SQL)

## Database Schema

```mermaid
erDiagram
    users {
        int user_id PK
        string full_name
        string email
        string bio
        timestamp created_at
    }

    roles {
        int role_id PK
        string name
        string description
        int max_active_paths
    }

    actions {
        int action_id PK
        string action_key
        string description
    }

    role_actions {
        int role_id FK
        int action_id FK
    }

    user_roles {
        int user_id FK
        int role_id FK
    }

    teams {
        int team_id PK
        string name
        int manager_user_id FK
    }

    team_members {
        int team_id FK
        int user_id FK
    }

    careers {
        int career_id PK
        string name
        string specialization
    }

    path_templates {
        int path_template_id PK
        int career_id FK
        string name
        string description
        int duration_hours
    }

    path_template_steps {
        int step_id PK
        int path_template_id FK
        int step_order
        string name
        string description
        int duration_hours
        string course_link
    }

    path_step_dependencies {
        int step_id FK
        int depends_on_step_id FK
    }

    user_career_paths {
        int user_career_path_id PK
        int user_id FK
        int career_id FK
        date start_date
        date end_date
        int overall_progress_percent
    }

    user_path_assignments {
        int user_path_assignment_id PK
        int user_career_path_id FK
        int path_template_id FK
        date start_date
        date deadline
        string status
        int progress_percent
        string mentor_validation_status
    }

    user_step_progress {
        int user_step_progress_id PK
        int user_path_assignment_id FK
        int step_id FK
        string status
        int progress_percent
        date planned_start_date
        date planned_end_date
        date actual_start_date
        date actual_end_date
        timestamp updated_at
    }

    log_entries {
        int log_entry_id PK
        int user_id FK
        int user_career_path_id FK
        string entry_type
        date entry_date
        string notes
        int related_user_path_assignment_id FK
    }

    %% Relationships
    roles ||--o{ role_actions : has
    actions ||--o{ role_actions : granted_to
    users ||--o{ user_roles : has
    roles ||--o{ user_roles : assigned_to

    users ||--o{ teams : manages
    teams ||--o{ team_members : contains

    careers ||--o{ path_templates : contains
    path_templates ||--o{ path_template_steps : has
    path_template_steps ||--o{ path_step_dependencies : depends_on

    users ||--o{ user_career_paths : assigned
    careers ||--o{ user_career_paths : defines
    user_career_paths ||--o{ user_path_assignments : includes
    path_templates ||--o{ user_path_assignments : instantiates
    user_path_assignments ||--o{ user_step_progress : tracks
    path_template_steps ||--o{ user_step_progress : references

    users ||--o{ log_entries : writes
    user_career_paths ||--o{ log_entries : about
    user_path_assignments ||--o{ log_entries : related_to
```

### Schema Explanation

The schema is organized into **4 main domains**:

#### 1. Users & Access Control

```mermaid
flowchart LR
    subgraph access [Access Control]
        U[users] --> UR[user_roles]
        UR --> R[roles]
        R --> RA[role_actions]
        RA --> A[actions]
    end
```

| Table | Purpose |
|-------|---------|
| `users` | All people in the system (admins, mentors, mentees, path creators) |
| `roles` | System roles: admin, path_creator, mentor, mentee. Includes `max_active_paths` to limit concurrent assignments |
| `actions` | Atomic permissions like `team.view`, `paths.assign`, `paths.validate` |
| `role_actions` | Maps which actions each role can perform |
| `user_roles` | Assigns roles to users. A user can have multiple roles |

#### 2. Team Organization

```mermaid
flowchart LR
    subgraph teams_org [Team Structure]
        U[users] -->|manages| T[teams]
        T --> TM[team_members]
        TM --> U2[users]
    end
```

| Table | Purpose |
|-------|---------|
| `teams` | Groups of users managed by a single manager |
| `team_members` | Links users to teams. A user can belong to multiple teams |

#### 3. Learning Path Templates (Catalog)

```mermaid
flowchart TD
    C[careers] --> PT[path_templates]
    PT --> PTS[path_template_steps]
    PTS --> PSD[path_step_dependencies]
```

| Table | Purpose |
|-------|---------|
| `careers` | High-level career tracks (e.g., "Frontend Developer", "UX/UI Designer") |
| `path_templates` | Reusable learning paths belonging to a career. Seniority encoded in name |
| `path_template_steps` | Individual learning activities within a path (courses, modules) |
| `path_step_dependencies` | Prerequisites between steps - a step can only start after dependencies are completed |

#### 4. User Progress & Tracking

This is where **templates become real assignments**. Think of it like a university degree:

```mermaid
flowchart TD
    subgraph career [user_career_paths = Degree Program]
        UCP["John pursues UX/UI Designer<br/>Jan 14 - Jun 14, 2025"]
    end

    subgraph paths [user_path_assignments = Courses]
        P1["Path 1: User Research<br/>Jan 14 - Feb 14"]
        P2["Path 2: Design Thinking<br/>Feb 15 - Mar 15"]
        P3["Path 3: Prototyping<br/>Mar 16 - Apr 16"]
    end

    subgraph steps [user_step_progress = Lessons]
        S1[Research planning]
        S2[Interview guide]
        S3[Conduct interviews]
    end

    UCP --> P1
    UCP --> P2
    UCP --> P3
    P1 --> S1
    P1 --> S2
    P1 --> S3
```

| Level | Table | Analogy | Example |
|-------|-------|---------|---------|
| Career | `user_career_paths` | Degree Program | "John is pursuing UX/UI Designer from Jan-Jun 2025" |
| Path | `user_path_assignments` | Courses in the program | "Course 1: User Research Fundamentals (4 weeks)" |
| Step | `user_step_progress` | Lessons in each course | "Lesson 1: Research planning (6 hours)" |

| Table | Purpose |
|-------|---------|
| `user_career_paths` | When a user is assigned to pursue a career track with start/end dates |
| `user_path_assignments` | Concrete assignment of a path template to a user's career journey |
| `user_step_progress` | Tracks progress on each step with planned vs actual dates |
| `log_entries` | Logbook for mentor-mentee interactions, approvals, and notes |

#### Complete Data Flow

```mermaid
flowchart TB
    subgraph catalog [Template Catalog - Created Once]
        C[careers] --> PT[path_templates]
        PT --> PTS[path_template_steps]
        PTS --> PSD[path_step_dependencies]
    end

    subgraph assignment [User Assignments - Per Person]
        U[users] --> UCP[user_career_paths]
        C --> UCP
        UCP --> UPA[user_path_assignments]
        PT --> UPA
        UPA --> USP[user_step_progress]
        PTS --> USP
    end

    subgraph feedback [Feedback Loop]
        UCP --> LOG[log_entries]
        UPA --> LOG
    end
```

**The flow is**:
1. **Admins/Path Creators** define careers, paths, and steps
2. **Mentors** assign career paths to mentees
3. **System** creates `user_career_paths` → `user_path_assignments` → `user_step_progress`
4. **Mentees** work through steps, updating progress
5. **Mentors** validate completed paths and add log entries

## Project Structure

```
upskilling/
├── db/
│   ├── schema.sql      # Database table definitions
│   └── seed.sql        # Demo data for development
├── docs/
│   └── db/
│       └── tables.md   # Quick reference for tables
└── README.md
```

## Getting Started

1. **Database Setup**
   ```bash
   # Run schema creation
   psql -d your_db -f db/schema.sql
   
   # Load demo data
   psql -d your_db -f db/seed.sql
   ```

2. **Backend** (coming soon)
3. **Frontend** (coming soon)

## License

Internal use only.
