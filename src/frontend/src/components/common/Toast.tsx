import { useEffect } from "react";

export type ToastType = "success" | "error" | "warning";

interface ToastProps {
  message: string;
  type: ToastType;
  icon?: string;
  onClose: () => void;
}

const Toast = ({ message, type, icon, onClose }: ToastProps) => {
  // Chiudi automaticamente dopo 3 secondi
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, [onClose]);

  const baseClasses =
    "fixed left-1/2 -translate-x-1/2 top-6 px-6 py-4 rounded-lg text-sm z-50 shadow-lg " +
    "flex items-center justify-center gap-2 min-w-[200px] text-center animate-slideDown";

  const typeClasses = {
    success: "bg-green-500 text-white",
    error: "bg-red-500 text-white",
    warning: "bg-yellow-50 text-gray-900",
  };

  return (
    <div className={`${baseClasses} ${typeClasses[type]}`}>
      {icon && <i className={`fas ${icon}`} />}
      {message}
    </div>
  );
};

export default Toast;
