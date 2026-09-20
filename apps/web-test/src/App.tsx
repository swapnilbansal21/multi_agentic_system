import { useState } from "react";
import {
  agentQuery,
  confirmMeeting,
  suggestSlots,
  ApiError,
  type SlotSuggestion,
} from "./api";

const styles: Record<string, React.CSSProperties> = {
  page: { fontFamily: "sans-serif", maxWidth: 720, margin: "2rem auto", padding: "0 1rem" },
  section: { border: "1px solid #ccc", borderRadius: 8, padding: "1rem", marginBottom: "1.5rem" },
  row: { display: "flex", gap: "0.5rem", marginBottom: "0.5rem", flexWrap: "wrap" },
  input: { flex: 1, padding: "0.4rem", minWidth: 160 },
  button: { padding: "0.5rem 1rem", cursor: "pointer" },
  slot: { border: "1px solid #ddd", borderRadius: 6, padding: "0.5rem", marginBottom: "0.5rem" },
  error: { color: "#b00020", whiteSpace: "pre-wrap" },
  pre: { background: "#f5f5f5", padding: "0.75rem", borderRadius: 6, overflowX: "auto" },
};

function SuggestSlotsSection() {
  const [attendees, setAttendees] = useState("swapnil.bansal@secninjaz.com");
  const [duration, setDuration] = useState(30);
  const [daysAhead, setDaysAhead] = useState(7);
  const [slots, setSlots] = useState<SlotSuggestion[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirmedFor, setConfirmedFor] = useState<string | null>(null);

  const handleSuggest = async () => {
    setError(null);
    setSlots(null);
    setLoading(true);
    try {
      const emails = attendees.split(",").map((a) => a.trim()).filter(Boolean);
      const res = await suggestSlots(emails, duration, daysAhead);
      setSlots(res.suggested_slots);
    } catch (e) {
      setError(e instanceof ApiError ? `[${e.status}] ${e.message}` : String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (slot: SlotSuggestion) => {
    setError(null);
    try {
      const emails = attendees.split(",").map((a) => a.trim()).filter(Boolean);
      const res = await confirmMeeting({
        organizerCalendarId: emails[0] ?? "primary",
        summary: "Test meeting from web-test UI",
        description: "Created via SMMS-Agent web test frontend",
        start: slot.start,
        end: slot.end,
        attendees: emails,
      });
      setConfirmedFor(`${slot.start} → event ${res.event_id} (${res.status})`);
    } catch (e) {
      setError(e instanceof ApiError ? `[${e.status}] ${e.message}` : String(e));
    }
  };

  return (
    <section style={styles.section}>
      <h2>1. Suggest Slots (Scheduler agent → mcp-calendar → Google Calendar)</h2>
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        Attendees here must be real email addresses — this endpoint bypasses the LLM
        name→email resolution (that only happens via the natural-language box below).
      </p>
      <div style={styles.row}>
        <input
          style={styles.input}
          value={attendees}
          onChange={(e) => setAttendees(e.target.value)}
          placeholder="comma-separated attendee emails"
        />
      </div>
      <div style={styles.row}>
        <input
          style={styles.input}
          type="number"
          value={duration}
          onChange={(e) => setDuration(Number(e.target.value))}
          placeholder="duration (minutes)"
        />
        <input
          style={styles.input}
          type="number"
          value={daysAhead}
          onChange={(e) => setDaysAhead(Number(e.target.value))}
          placeholder="days ahead"
        />
        <button style={styles.button} onClick={handleSuggest} disabled={loading}>
          {loading ? "Loading..." : "Find Slots"}
        </button>
      </div>

      {error && <p style={styles.error}>{error}</p>}
      {confirmedFor && <p style={{ color: "green" }}>Confirmed: {confirmedFor}</p>}

      {slots && slots.length === 0 && <p>No free slots found.</p>}
      {slots?.map((slot, i) => (
        <div key={i} style={styles.slot}>
          <div>
            {slot.start} → {slot.end}
          </div>
          <div>
            Confidence: {slot.confidence} ({slot.attendees_free}/{slot.attendees_total} free)
          </div>
          <button style={styles.button} onClick={() => handleConfirm(slot)}>
            Confirm & Send Invite
          </button>
        </div>
      ))}
    </section>
  );
}

function AgentQuerySection() {
  const [query, setQuery] = useState("schedule a meeting with Swapnil about budget review");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await agentQuery(query);
      setResult(JSON.stringify(res, null, 2));
    } catch (e) {
      setError(e instanceof ApiError ? `[${e.status}] ${e.message}` : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section style={styles.section}>
      <h2>2. Natural language (Supervisor → name resolution → agent)</h2>
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        Needs Azure OpenAI credentials configured in apps/api/.env — will error otherwise.
      </p>
      <div style={styles.row}>
        <input
          style={styles.input}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button style={styles.button} onClick={handleAsk} disabled={loading}>
          {loading ? "Loading..." : "Ask"}
        </button>
      </div>
      {error && <p style={styles.error}>{error}</p>}
      {result && <pre style={styles.pre}>{result}</pre>}
    </section>
  );
}

export default function App() {
  return (
    <div style={styles.page}>
      <h1>SMMS-Agent — Web Test</h1>
      <SuggestSlotsSection />
      <AgentQuerySection />
    </div>
  );
}
