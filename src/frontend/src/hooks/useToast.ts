import { useState, useCallback } from "react";
import { ToastType } from "../components/common/Toast";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
  icon?: string;
}

let toastId = 0;

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback(
    (message: string, type: ToastType = "success", icon?: string) => {
      const id = toastId++;
      setToasts((prev) => [...prev, { id, message, type, icon }]);
    },
    []
  );

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return {
    toasts,
    showToast,
    removeToast,
  };
};

export default useToast;
