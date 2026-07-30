/**
 * Frontend display helper mirroring backend/apps/warehouse/services/masking.py.
 * The API already masks fields server-side based on role; this is used for
 * client-side "preview as another role" toggles and any client-composed text.
 *
 *   MBR-10039281      -> MBR-••••9281
 *   CLM-2026-000938   -> CLM-••••0938
 */
const MASK_CHAR = "•"; // •

export function maskIdentifier(value: string | null | undefined): string {
  if (!value) return value ?? "";
  const parts = value.split("-");
  if (parts.length < 2) {
    return value.length > 4 ? `${MASK_CHAR.repeat(4)}${value.slice(-4)}` : MASK_CHAR.repeat(value.length);
  }
  const [prefix, ...rest] = parts;
  const remainder = rest.join("");
  const suffix = remainder.length >= 4 ? remainder.slice(-4) : remainder;
  return `${prefix}-${MASK_CHAR.repeat(4)}${suffix}`;
}

export function maskEmail(value: string | null | undefined): string {
  if (!value || !value.includes("@")) return MASK_CHAR.repeat(8);
  const [local, domain] = value.split("@");
  return `${local[0] ?? ""}${MASK_CHAR.repeat(3)}@${domain}`;
}

export function maskPhone(value: string | null | undefined): string {
  if (!value) return value ?? "";
  const digits = value.replace(/\D/g, "");
  const last4 = digits.length >= 4 ? digits.slice(-4) : digits;
  return `${MASK_CHAR.repeat(3)}-${MASK_CHAR.repeat(3)}-${last4}`;
}
