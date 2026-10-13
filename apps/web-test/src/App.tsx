import { useState } from "react";
import { useIsAuthenticated, useMsal } from "@azure/msal-react";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import {
  agentQuery,
  confirmMeeting,
  suggestSlots,
  ApiError,
  type SlotSuggestion,
} from "./api";
import { loginRequest } from "./authConfig";

// Acquires a fresh access token for calling the API, refreshing silently in
// the background and only falling back to an interactive popup if the
// silent refresh fails (e.g. the session truly expired).
function useAccessToken() {
  const { instance, accounts } = useMsal();

  return async (): Promise<string> => {
    const account = accounts[0];
    try {
      const result = await instance.acquireTokenSilent({ ...loginRequest, account });
      return result.accessToken;
    } catch (e) {
      if (e instanceof InteractionRequiredAuthError) {
        const result = await instance.acquireTokenPopup(loginRequest);
        return result.accessToken;
      }
      throw e;
    }
  };
}

const FONT_STACK =
  "'Segoe UI', system-ui, -apple-system, sans-serif";

const styles: Record<string, React.CSSProperties> = {
  body: {
    minHeight: "100vh",
    background: "linear-gradient(180deg, #f3f6fb 0%, #eef1f7 100%)",
    fontFamily: FONT_STACK,
  },
  page: { maxWidth: 760, margin: "0 auto", padding: "2.5rem 1.25rem 4rem" },
  header: { marginBottom: "2rem" },
  title: {
    margin: 0,
    fontSize: "1.9rem",
    fontWeight: 700,
    color: "#1a2b4c",
    letterSpacing: "-0.02em",
  },
  badge: {
    display: "inline-block",
    marginTop: "0.5rem",
    padding: "0.2rem 0.6rem",
    fontSize: "0.72rem",
    fontWeight: 600,
    color: "#3457d5",
    background: "#e8edfc",
    borderRadius: 999,
    letterSpacing: "0.03em",
  },
  subtitle: { margin: "0.6rem 0 0", color: "#5b6577", fontSize: "0.95rem" },
  section: {
    background: "#ffffff",
    border: "1px solid #e3e7ef",
    borderRadius: 14,
    padding: "1.5rem",
    marginBottom: "1.5rem",
    boxShadow: "0 1px 3px rgba(20, 30, 60, 0.06)",
  },
  sectionTitle: {
    margin: "0 0 0.35rem",
    fontSize: "1.05rem",
    color: "#1a2b4c",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
  },
  stepNumber: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: 22,
    height: 22,
    borderRadius: "50%",
    background: "#3457d5",
    color: "#fff",
    fontSize: "0.75rem",
    fontWeight: 700,
    flexShrink: 0,
  },
  hint: { fontSize: "0.83rem", color: "#7a8296", margin: "0 0 1rem", lineHeight: 1.5 },
  row: { display: "flex", gap: "0.6rem", marginBottom: "0.7rem", flexWrap: "wrap" },
  input: {
    flex: 1,
    padding: "0.55rem 0.7rem",
    minWidth: 160,
    border: "1px solid #d7dce6",
    borderRadius: 8,
    fontSize: "0.9rem",
    fontFamily: FONT_STACK,
    outline: "none",
    background: "#fbfcfe",
  },
  button: {
    padding: "0.55rem 1.1rem",
    cursor: "pointer",
    border: "none",
    borderRadius: 8,
    background: "#3457d5",
    color: "#fff",
    fontSize: "0.9rem",
    fontWeight: 600,
    fontFamily: FONT_STACK,
    transition: "background 0.15s ease",
  },
  slot: {
    border: "1px solid #e3e7ef",
    borderRadius: 10,
    padding: "0.75rem 0.9rem",
    marginBottom: "0.6rem",
    background: "#fafbfd",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "0.75rem",
    flexWrap: "wrap",
  },
  slotConfidence: { fontSize: "0.82rem", color: "#5b6577" },
  error: {
    color: "#b00020",
    background: "#fdecee",
    border: "1px solid #f6c6cd",
    borderRadius: 8,
    padding: "0.6rem 0.8rem",
    whiteSpace: "pre-wrap",
    fontSize: "0.87rem",
  },
  success: {
    color: "#1e7a3e",
    background: "#e9f7ee",
    border: "1px solid #bfe6cc",
    borderRadius: 8,
    padding: "0.6rem 0.8rem",
    fontSize: "0.87rem",
  },
  pre: {
    background: "#f6f7fb",
    border: "1px solid #e3e7ef",
    padding: "0.85rem",
    borderRadius: 8,
    overflowX: "auto",
    fontSize: "0.82rem",
  },
};

function SuggestSlotsSection() {
  const getAccessToken = useAccessToken();
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
      const token = await getAccessToken();
      const emails = attendees.split(",").map((a) => a.trim()).filter(Boolean);
      const res = await suggestSlots(token, emails, duration, daysAhead);
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
      const token = await getAccessToken();
      const emails = attendees.split(",").map((a) => a.trim()).filter(Boolean);
      const res = await confirmMeeting(token, {
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
      <h2 style={styles.sectionTitle}>
        <span style={styles.stepNumber}>1</span>
        Suggest Slots
      </h2>
      <p style={styles.hint}>
        Scheduler agent → mcp-calendar → Google Calendar. Attendees here must be real
        email addresses — this endpoint bypasses the LLM name→email resolution (that
        only happens via the natural-language box below).
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
          {loading ? "Loading…" : "Find Slots"}
        </button>
      </div>

      {error && <p style={styles.error}>{error}</p>}
      {confirmedFor && <p style={styles.success}>✓ Confirmed: {confirmedFor}</p>}

      {slots && slots.length === 0 && <p style={styles.hint}>No free slots found.</p>}
      {slots?.map((slot, i) => (
        <div key={i} style={styles.slot}>
          <div>
            <div style={{ fontWeight: 600, color: "#1a2b4c" }}>
              {slot.start} → {slot.end}
            </div>
            <div style={styles.slotConfidence}>
              Confidence: {slot.confidence} ({slot.attendees_free}/{slot.attendees_total} free)
            </div>
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
  const getAccessToken = useAccessToken();
  const [query, setQuery] = useState("schedule a meeting with Swapnil about budget review");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const token = await getAccessToken();
      const res = await agentQuery(token, query);
      setResult(JSON.stringify(res, null, 2));
    } catch (e) {
      setError(e instanceof ApiError ? `[${e.status}] ${e.message}` : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section style={styles.section}>
      <h2 style={styles.sectionTitle}>
        <span style={styles.stepNumber}>2</span>
        Natural Language
      </h2>
      <p style={styles.hint}>
        Supervisor → name resolution → agent. Needs Azure OpenAI credentials
        configured in apps/api/.env — will error otherwise.
      </p>
      <div style={styles.row}>
        <input
          style={styles.input}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button style={styles.button} onClick={handleAsk} disabled={loading}>
          {loading ? "Loading…" : "Ask"}
        </button>
      </div>
      {error && <p style={styles.error}>{error}</p>}
      {result && <pre style={styles.pre}>{result}</pre>}
    </section>
  );
}

function AuthBar() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  if (!isAuthenticated) {
    return (
      <button style={styles.button} onClick={() => instance.loginPopup(loginRequest)}>
        Sign in with Microsoft
      </button>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <span style={styles.hint}>Signed in as {accounts[0]?.username}</span>
      <button
        style={{ ...styles.button, background: "#5b6577" }}
        onClick={() => instance.logoutPopup()}
      >
        Sign out
      </button>
    </div>
  );
}

export default function App() {
  const isAuthenticated = useIsAuthenticated();

  return (
    <div style={styles.body}>
      <div style={styles.page}>
        <header style={styles.header}>
          <h1 style={styles.title}>SMMS-Agent</h1>
          <span style={styles.badge}>WEB TEST HARNESS</span>
          <p style={styles.subtitle}>
            Quick manual test surface for the scheduling agents — not the production UI.
          </p>
        </header>
        <section style={styles.section}>
          <AuthBar />
        </section>
        {isAuthenticated && (
          <>
            <SuggestSlotsSection />
            <AgentQuerySection />
          </>
        )}
      </div>
    </div>
  );
}
