import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  BookOpen,
  GraduationCap,
  User,
  CheckSquare,
  Users,
  FileText,
  LogOut,
  Menu,
  X,
  Bell,
  ChevronLeft,
  ChevronRight,
  UserCog,
  Clock,
} from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: null },
  { name: 'Development Plans', href: '/development-plans', icon: BookOpen, roles: null },
  { name: 'Learning Paths', href: '/learning-paths', icon: GraduationCap, roles: null },
  { name: 'My Bio', href: '/my-bio', icon: User, roles: null },
  { name: 'Mentor Validation', href: '/mentor-validation', icon: CheckSquare, roles: ['admin', 'mentor'] },
  { name: 'Team Management', href: '/team-management', icon: Users, roles: ['admin', 'mentor'] },
  { name: 'Path Creation', href: '/path-creation', icon: FileText, roles: ['path_creator'] },
  { name: 'User Management', href: '/user-management', icon: UserCog, roles: ['admin'] },
];

// Example notifications
const exampleNotifications = [
  { id: 1, title: 'Path Approved', message: 'Your "React Fundamentals" path has been approved by your mentor.', time: '2 hours ago', read: false },
  { id: 2, title: 'New Assignment', message: 'You have been assigned a new learning path: JavaScript Basics.', time: '1 day ago', read: false },
  { id: 3, title: 'Deadline Reminder', message: 'Your "HTML & CSS" path deadline is in 3 days.', time: '2 days ago', read: true },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const notificationsRef = useRef<HTMLDivElement>(null);

  // Close notifications dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationsRef.current && !notificationsRef.current.contains(event.target as Node)) {
        setNotificationsOpen(false);
      }
    };
    if (notificationsOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [notificationsOpen]);

  // Filter navigation items based on user's roles
  const filteredNavigation = navigation.filter((item) => {
    if (!item.roles) return true; // null means accessible to all
    return user?.roles?.some((role) => item.roles.includes(role.name));
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50
          transform transition-all duration-300 ease-in-out
          lg:relative lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          ${sidebarCollapsed ? 'lg:w-16' : 'w-56'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo - Black header */}
          <div className="flex items-center justify-between h-16 px-4 bg-black flex-shrink-0">
            {!sidebarCollapsed && (
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-white">pwc</span>
                <span className="text-lg font-semibold text-primary-500">UpSkills</span>
              </div>
            )}
            {sidebarCollapsed && (
              <div className="flex items-center justify-center w-full">
                <span className="text-lg font-bold text-primary-500">U</span>
              </div>
            )}
            <button
              className="lg:hidden text-gray-400 hover:text-white"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* White section wrapper - contains nav, collapse button, and sign out */}
          <div className="flex-1 flex flex-col bg-white border-r border-gray-200">
            {/* Navigation */}
            <nav className="flex-1 py-4 overflow-y-auto">
              {filteredNavigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  title={sidebarCollapsed ? item.name : undefined}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'text-primary-500 bg-primary-50 border-l-4 border-primary-500'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50 border-l-4 border-transparent'
                    } ${sidebarCollapsed ? 'justify-center px-2' : ''}`
                  }
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  {!sidebarCollapsed && <span>{item.name}</span>}
                </NavLink>
              ))}
            </nav>

            {/* Collapse button - Desktop only */}
            <div className="hidden lg:block p-2 border-t border-gray-200 flex-shrink-0">
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="w-full flex items-center justify-center p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              >
                {sidebarCollapsed ? (
                  <ChevronRight className="w-5 h-5" />
                ) : (
                  <ChevronLeft className="w-5 h-5" />
                )}
              </button>
            </div>

            {/* User section */}
            <div className="p-2 border-t border-gray-200 flex-shrink-0">
              <button
                onClick={handleLogout}
                title={sidebarCollapsed ? 'Sign out' : undefined}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-600 hover:text-danger-600 hover:bg-danger-50 transition-all duration-200 ${
                  sidebarCollapsed ? 'justify-center px-2' : ''
                }`}
              >
                <LogOut className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>Sign out</span>}
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between h-16 px-4 lg:px-6 bg-black text-white">
          <div className="flex items-center gap-4">
            <button
              className="lg:hidden p-2 text-gray-300 hover:text-white"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Notifications */}
            <div className="relative" ref={notificationsRef}>
              <button 
                className="relative p-2 text-gray-300 hover:text-white"
                onClick={() => setNotificationsOpen(!notificationsOpen)}
              >
                <Bell className="w-5 h-5" />
                {exampleNotifications.filter(n => !n.read).length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-dropdown border border-gray-200 z-50">
                  <div className="px-4 py-3 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {exampleNotifications.map((notification) => (
                      <div 
                        key={notification.id}
                        className={`px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0 ${
                          !notification.read ? 'bg-primary-50/50' : ''
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                            !notification.read ? 'bg-primary-500' : 'bg-gray-300'
                          }`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                            <p className="text-sm text-gray-500 mt-0.5">{notification.message}</p>
                            <div className="flex items-center gap-1 mt-1 text-xs text-gray-400">
                              <Clock className="w-3 h-3" />
                              <span>{notification.time}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="px-4 py-3 border-t border-gray-200">
                    <button className="w-full text-sm text-primary-500 hover:text-primary-600 font-medium">
                      View all notifications
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            {/* User Avatar - Clickable to go to My Bio */}
            <button 
              onClick={() => navigate('/my-bio')}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
              title="Go to My Bio"
            >
              <div className="w-9 h-9 rounded-full bg-primary-500 flex items-center justify-center">
                <span className="text-white font-semibold text-sm">
                  {user?.fullName?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                </span>
              </div>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-gray-50">
          <div className="container mx-auto px-4 lg:px-8 py-8 max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
