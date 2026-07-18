export const SESSION_INVALIDATED_EVENT = "tourhub:session-invalidated";

export function notifySessionInvalidated(): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event(SESSION_INVALIDATED_EVENT));
}
