const API_BASE = "http://localhost:8000";

export type SlotSuggestion = {
  start: string;
  end: string;
  attendees_free: number;
  attendees_total: number;
  confidence: number;
};

export type SuggestResponse = {
  agent: string;
  suggested_slots: SlotSuggestion[];
  attendees: string[];
};

export type ConfirmResponse = {
  event_id: string;
  html_link: string;
  status: string;
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function postJson<T>(path: string, body: unknown, token: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new ApiError(res.status, data.detail ?? data.error ?? "Request failed");
  }
  return data as T;
}

export function suggestSlots(
  token: string,
  attendees: string[],
  durationMinutes: number,
  daysAhead: number
): Promise<SuggestResponse> {
  return postJson<SuggestResponse>(
    "/schedule-meeting/suggest",
    { attendees, duration_minutes: durationMinutes, days_ahead: daysAhead },
    token
  );
}

export function confirmMeeting(
  token: string,
  params: {
    organizerCalendarId: string;
    summary: string;
    description: string;
    start: string;
    end: string;
    attendees: string[];
  }
): Promise<ConfirmResponse> {
  return postJson<ConfirmResponse>(
    "/schedule-meeting/confirm",
    {
      organizer_calendar_id: params.organizerCalendarId,
      summary: params.summary,
      description: params.description,
      start: params.start,
      end: params.end,
      attendees: params.attendees,
    },
    token
  );
}

export function agentQuery(token: string, query: string): Promise<unknown> {
  return postJson<unknown>("/agent/query", { query }, token);
}
