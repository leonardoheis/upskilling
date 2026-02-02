// User types
export interface Role {
  roleId: number;
  name: string;
  description: string | null;
  maxActivePaths: number | null;
}

export interface User {
  userId: number;
  fullName: string;
  email: string;
  bio: string | null;
  createdAt: string;
  roles: Role[];
}

export interface UserWithPermissions extends User {
  permissions: string[];
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  fullName: string;
  email: string;
  password: string;
  bio?: string;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

export interface AuthResponse {
  user: User;
  tokens: TokenResponse;
}

// Team types
export interface Team {
  teamId: number;
  name: string;
  managerUserId: number;
}

export interface TeamMember {
  userId: number;
  fullName: string;
  email: string;
}

export interface TeamWithMembers extends Team {
  manager: User;
  members: TeamMember[];
}

export interface TeamListItem {
  teamId: number;
  name: string;
  memberCount: number;
  managerName: string;
}

// Career types
export interface Career {
  careerId: number;
  name: string;
  specialization: string | null;
}

export interface CareerWithPaths extends Career {
  pathTemplates: PathTemplate[];
}

// Path types
export interface PathTemplate {
  pathTemplateId: number;
  careerId: number;
  name: string;
  description: string;
  durationHours: number;
  defaultStartOffsetDays: number | null;
  defaultDeadlineOffsetDays: number | null;
}

export interface PathStepDependency {
  dependsOnStepId: number;
  dependsOnStepName: string;
}

export interface PathStep {
  stepId: number;
  pathTemplateId: number;
  stepOrder: number;
  name: string;
  description: string | null;
  durationHours: number | null;
  courseLink: string | null;
  dependencies: PathStepDependency[];
}

export interface PathTemplateWithSteps extends PathTemplate {
  steps: PathStep[];
}

// Progress types
export interface UserCareerPath {
  userCareerPathId: number;
  userId: number;
  careerId: number;
  startDate: string;
  endDate: string;
  overallProgressPercent: number;
}

export interface UserCareerPathDetail extends UserCareerPath {
  careerName: string;
  careerSpecialization: string | null;
  pathAssignments: UserPathAssignment[];
}

export interface UserPathAssignment {
  userPathAssignmentId: number;
  userCareerPathId: number;
  pathTemplateId: number;
  startDate: string;
  deadline: string;
  status: 'Pending' | 'In Progress' | 'Completed';
  progressPercent: number;
  mentorValidationStatus: 'Pending' | 'Approved' | 'Rejected';
}

export interface UserPathAssignmentDetail extends UserPathAssignment {
  pathTemplate: PathTemplate;
  stepProgress: UserStepProgress[];
}

export interface UserStepProgress {
  userStepProgressId: number;
  userPathAssignmentId: number;
  stepId: number;
  status: 'Pending' | 'In Progress' | 'Completed';
  progressPercent: number;
  plannedStartDate: string | null;
  plannedEndDate: string | null;
  actualStartDate: string | null;
  actualEndDate: string | null;
  updatedAt: string;
  step: PathStep | null;
}

export interface DashboardStats {
  currentCareer: string | null;
  currentPath: string | null;
  currentPathProgress: number;
  pathsRemaining: number;
  overallProgress: number;
  skillsObtained: number;
}

export interface MenteeProgressSummary {
  userId: number;
  fullName: string;
  email: string;
  careerName: string;
  startDate: string;
  endDate: string;
  overallProgressPercent: number;
  pathsCompleted: number;
  pathsTotal: number;
  pendingValidation: number;
}

// Log entry types
export interface LogEntry {
  logEntryId: number;
  userId: number;
  userCareerPathId: number;
  entryType: string;
  entryDate: string;
  notes: string;
  relatedUserPathAssignmentId: number | null;
}

export interface LogEntryDetail extends LogEntry {
  userName: string;
  pathName: string | null;
}

// API response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface MessageResponse {
  message: string;
  detail?: string;
}
