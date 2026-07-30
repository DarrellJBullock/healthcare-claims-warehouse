import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: "bg-accent-500 text-surface-950 hover:bg-accent-400",
  secondary: "bg-surface-700 text-slate-100 hover:bg-surface-600 border border-surface-600",
  ghost: "bg-transparent text-slate-300 hover:bg-surface-800 border border-transparent",
  danger: "bg-risk-critical/90 text-white hover:bg-risk-critical",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  return (
    <button
      className={`focus-ring inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    />
  );
}
