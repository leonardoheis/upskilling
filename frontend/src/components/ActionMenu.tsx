import { MoreVertical } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface ActionMenuItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  danger?: boolean;
}

interface ActionMenuProps {
  items: ActionMenuItem[];
}

export default function ActionMenu({ items }: ActionMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ top: 0, right: 0 });
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Calculate menu position when opened
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setMenuPosition({
        top: rect.bottom + 8,
        right: window.innerWidth - rect.right,
      });
    }
  }, [isOpen]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node) &&
          buttonRef.current && !buttonRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="relative" ref={menuRef}>
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <MoreVertical className="w-5 h-5" />
      </button>

      {isOpen && (
        <div 
          className="fixed w-48 bg-white border border-gray-200 rounded-lg shadow-dropdown z-[9999]"
          style={{ top: menuPosition.top, right: menuPosition.right }}
        >
          {items.map((item, index) => (
            <button
              key={index}
              onClick={() => {
                item.onClick();
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-2 px-4 py-2 text-sm text-left transition-colors
                ${item.danger ? 'text-danger-600 hover:bg-danger-50' : 'text-gray-700 hover:bg-gray-50'}
                ${index === 0 ? 'rounded-t-lg' : ''}
                ${index === items.length - 1 ? 'rounded-b-lg' : ''}
              `}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
