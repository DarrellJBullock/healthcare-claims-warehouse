export type BadgeTone = "neutral" | "success" | "warning" | "danger" | "info";

export function claimStatusTone(status: string): BadgeTone {
  switch (status) {
    case "Paid":
      return "success";
    case "Denied":
      return "danger";
    case "Pending":
      return "warning";
    case "Partially Paid":
      return "info";
    default:
      return "neutral";
  }
}

export function severityTone(severity: string): BadgeTone {
  switch (severity) {
    case "HIGH":
      return "danger";
    case "MEDIUM":
      return "warning";
    case "LOW":
      return "info";
    default:
      return "neutral";
  }
}
