interface FilterOption {
  id: string;
  label: string;
  color?: string;
}

interface FilterButtonsProps {
  options: FilterOption[];
  activeId: string;
  onChange: (id: string) => void;
}

export default function FilterButtons({ options, activeId, onChange }: FilterButtonsProps) {
  const colorClasses: Record<string, { active: string; inactive: string }> = {
    primary: {
      active: 'bg-primary-500 text-white border-primary-500',
      inactive: 'bg-white text-primary-500 border-primary-500 hover:bg-primary-50',
    },
    success: {
      active: 'bg-success-500 text-white border-success-500',
      inactive: 'bg-white text-success-600 border-success-500 hover:bg-success-50',
    },
    warning: {
      active: 'bg-warning-500 text-white border-warning-500',
      inactive: 'bg-white text-warning-600 border-warning-500 hover:bg-warning-50',
    },
    danger: {
      active: 'bg-danger-500 text-white border-danger-500',
      inactive: 'bg-white text-danger-600 border-danger-500 hover:bg-danger-50',
    },
    gray: {
      active: 'bg-gray-700 text-white border-gray-700',
      inactive: 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50',
    },
  };

  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isActive = activeId === option.id;
        const color = option.color || 'primary';
        const classes = colorClasses[color] || colorClasses.primary;

        return (
          <button
            key={option.id}
            onClick={() => onChange(option.id)}
            className={`px-4 py-2 text-sm font-medium rounded-full border transition-all duration-200 ${
              isActive ? classes.active : classes.inactive
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
