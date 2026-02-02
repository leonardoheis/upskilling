import { useEffect, useState, useCallback } from 'react';
import { usersApi, authApi } from '../services/api';
import type { User } from '../types';
import { UserPlus, Users, Shield, X, Save } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ActionMenu from '../components/ActionMenu';

const AVAILABLE_ROLES = ['admin', 'mentor', 'mentee', 'path_creator'];

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [showEditRolesModal, setShowEditRolesModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);

  // New user form
  const [newUser, setNewUser] = useState({
    fullName: '',
    email: '',
    password: '',
    bio: '',
  });
  const [newUserRoles, setNewUserRoles] = useState<string[]>(['mentee']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const fetchUsers = useCallback(async () => {
    try {
      const response = await usersApi.list(1, 100);
      setUsers(response.items);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      // First register the user (creates with mentee role by default)
      const response = await authApi.register({
        fullName: newUser.fullName,
        email: newUser.email,
        password: newUser.password,
        bio: newUser.bio || undefined,
      });

      const userId = response.user.userId;

      // Assign additional roles (mentee is already assigned by default)
      for (const role of newUserRoles) {
        if (role !== 'mentee') {
          await usersApi.assignRole(userId, role);
        }
      }

      // If mentee was not selected, remove it
      if (!newUserRoles.includes('mentee')) {
        await usersApi.removeRole(userId, 'mentee');
      }

      // Reset form and refresh
      setShowAddUserModal(false);
      setNewUser({ fullName: '', email: '', password: '', bio: '' });
      setNewUserRoles(['mentee']);
      fetchUsers();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to create user');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditRoles = (user: User) => {
    setSelectedUser(user);
    setSelectedRoles(user.roles.map((r) => r.name));
    setShowEditRolesModal(true);
  };

  const handleSaveRoles = async () => {
    if (!selectedUser) return;
    setIsSubmitting(true);
    setError('');

    try {
      const currentRoles = selectedUser.roles.map((r) => r.name);
      
      // Roles to add
      const rolesToAdd = selectedRoles.filter((r) => !currentRoles.includes(r));
      // Roles to remove
      const rolesToRemove = currentRoles.filter((r) => !selectedRoles.includes(r));

      for (const role of rolesToAdd) {
        await usersApi.assignRole(selectedUser.userId, role);
      }

      for (const role of rolesToRemove) {
        await usersApi.removeRole(selectedUser.userId, role);
      }

      setShowEditRolesModal(false);
      setSelectedUser(null);
      fetchUsers();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Failed to update roles');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      await usersApi.delete(userId);
      fetchUsers();
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      const errorMessage = axiosError.response?.data?.detail || 'Failed to delete user. Please try again.';
      alert(errorMessage);
    }
  };

  const toggleRole = (role: string, roles: string[], setRoles: (roles: string[]) => void) => {
    if (roles.includes(role)) {
      setRoles(roles.filter((r) => r !== role));
    } else {
      setRoles([...roles, role]);
    }
  };

  const getRoleBadgeColor = (roleName: string) => {
    switch (roleName) {
      case 'admin':
        return 'bg-danger-100 text-danger-700';
      case 'mentor':
        return 'bg-primary-100 text-primary-700';
      case 'path_creator':
        return 'bg-warning-100 text-warning-700';
      case 'mentee':
        return 'bg-success-100 text-success-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <p className="mt-1 text-gray-500">
          Manage users, create new accounts, and assign roles
        </p>
      </div>

      {/* Main content card */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">All Users</h2>
          <button
            onClick={() => setShowAddUserModal(true)}
            className="btn btn-primary flex items-center gap-2"
          >
            <UserPlus className="w-4 h-4" />
            Add User
          </button>
        </div>

        {users.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No users yet</h3>
            <p className="text-gray-500">Create your first user to get started.</p>
          </div>
        ) : (
          <div className="overflow-visible">
            <table className="table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Roles</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.userId}>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center">
                          <span className="text-white font-semibold">
                            {user.fullName.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <span className="font-medium text-gray-900">{user.fullName}</span>
                      </div>
                    </td>
                    <td className="text-gray-600">{user.email}</td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {user.roles.map((role) => (
                          <span
                            key={role.roleId}
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(role.name)}`}
                          >
                            {role.name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="text-gray-600">
                      {new Date(user.createdAt).toLocaleDateString()}
                    </td>
                    <td>
                      <ActionMenu
                        items={[
                          {
                            label: 'Edit Roles',
                            onClick: () => handleEditRoles(user),
                          },
                          {
                            label: 'Delete User',
                            onClick: () => handleDeleteUser(user.userId),
                            danger: true,
                          },
                        ]}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add User Modal */}
      {showAddUserModal && (
        <>
          <div
            className="!fixed !inset-0 !m-0 bg-black/50 z-[9998]"
            onClick={() => setShowAddUserModal(false)}
          />
          <div className="!fixed !inset-y-0 !right-0 !m-0 w-full max-w-md bg-white shadow-modal z-[9999] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Add New User</h2>
              <button
                onClick={() => setShowAddUserModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddUser} className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {error && (
                  <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg text-danger-600 text-sm">
                    {error}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={newUser.fullName}
                    onChange={(e) => setNewUser({ ...newUser, fullName: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    className="input"
                    required
                    minLength={8}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bio (optional)
                  </label>
                  <textarea
                    value={newUser.bio}
                    onChange={(e) => setNewUser({ ...newUser, bio: e.target.value })}
                    className="input min-h-[80px]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Shield className="w-4 h-4 inline mr-2" />
                    Assign Roles
                  </label>
                  <div className="space-y-2">
                    {AVAILABLE_ROLES.map((role) => (
                      <label
                        key={role}
                        className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                      >
                        <input
                          type="checkbox"
                          checked={newUserRoles.includes(role)}
                          onChange={() => toggleRole(role, newUserRoles, setNewUserRoles)}
                          className="w-4 h-4 rounded border-gray-300 text-primary-500"
                        />
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(role)}`}>
                          {role}
                        </span>
                        <span className="text-sm text-gray-600">
                          {role === 'admin' && '- Full system access'}
                          {role === 'mentor' && '- Manage mentees and validate paths'}
                          {role === 'mentee' && '- Track learning progress'}
                          {role === 'path_creator' && '- Create and edit learning paths'}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </form>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowAddUserModal(false)}
                className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleAddUser}
                disabled={isSubmitting}
                className="btn btn-primary flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <LoadingSpinner size="sm" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Create User
                  </>
                )}
              </button>
            </div>
          </div>
        </>
      )}

      {/* Edit Roles Modal */}
      {showEditRolesModal && selectedUser && (
        <>
          <div
            className="!fixed !inset-0 !m-0 bg-black/50 z-[9998]"
            onClick={() => setShowEditRolesModal(false)}
          />
          <div className="!fixed !inset-y-0 !right-0 !m-0 w-full max-w-md bg-white shadow-modal z-[9999] flex flex-col">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Edit Roles</h2>
              <button
                onClick={() => setShowEditRolesModal(false)}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                {error && (
                  <div className="p-4 bg-danger-50 border border-danger-200 rounded-lg text-danger-600 text-sm">
                    {error}
                  </div>
                )}

                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                  <div className="w-12 h-12 rounded-full bg-primary-500 flex items-center justify-center">
                    <span className="text-white font-semibold text-lg">
                      {selectedUser.fullName.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{selectedUser.fullName}</h3>
                    <p className="text-sm text-gray-500">{selectedUser.email}</p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Shield className="w-4 h-4 inline mr-2" />
                    User Roles
                  </label>
                  <div className="space-y-2">
                    {AVAILABLE_ROLES.map((role) => (
                      <label
                        key={role}
                        className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50"
                      >
                        <input
                          type="checkbox"
                          checked={selectedRoles.includes(role)}
                          onChange={() => toggleRole(role, selectedRoles, setSelectedRoles)}
                          className="w-4 h-4 rounded border-gray-300 text-primary-500"
                        />
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(role)}`}>
                          {role}
                        </span>
                        <span className="text-sm text-gray-600">
                          {role === 'admin' && '- Full system access'}
                          {role === 'mentor' && '- Manage mentees and validate paths'}
                          {role === 'mentee' && '- Track learning progress'}
                          {role === 'path_creator' && '- Create and edit learning paths'}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowEditRolesModal(false)}
                className="btn bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveRoles}
                disabled={isSubmitting}
                className="btn btn-primary flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <LoadingSpinner size="sm" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Roles
                  </>
                )}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
