interface StatusBadgeProps {
  status: 'approved' | 'pending' | 'rejected' | 'completed' | 'in_progress';
  children?: React.ReactNode;
}

export default function StatusBadge({ status, children }: StatusBadgeProps) {
  const statusConfig = {
    approved: {
      bg: 'bg-success-100',
      text: 'text-success-700',
      label: 'Approved',
    },
    completed: {
      bg: 'bg-success-100',
      text: 'text-success-700',
      label: 'Completed',
    },
    pending: {
      bg: 'bg-warning-100',
      text: 'text-warning-700',
      label: 'Pending',
    },
    in_progress: {
      bg: 'bg-primary-100',
      text: 'text-primary-700',
      label: 'In Progress',
    },
    rejected: {
      bg: 'bg-danger-100',
      text: 'text-danger-700',
      label: 'Rejected',
    },
  };

  const config = statusConfig[status];

  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full ${config.bg} ${config.text}`}>
      {children || config.label}
    </span>
  );
}
