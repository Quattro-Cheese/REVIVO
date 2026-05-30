import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/client";

interface PredictData {
  focus: string;
  confidence: number;
  session_count: number;
}

interface SessionData {
  id: number;
  created_at: string;
  avg_bpm: number;
  avg_depth_cm: number;
  total_count: number;
  posture_correct_ratio: number;
  duration_sec: number;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username");
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [predict, setPredict] = useState<PredictData | null>(null);

  // useEffect 하나로 통합
  useEffect(() => {
    apiClient.get("/sessions/1").then((res) => setSessions(res.data));
    apiClient
      .get("/predict/1")
      .then((res) => setPredict(res.data))
      .catch(() => {});
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>👋 {username}님의 훈련 기록</h2>
        <button style={styles.logoutBtn} onClick={handleLogout}>
          로그아웃
        </button>
      </div>

      {predict && (
        <div style={styles.predictCard}>
          <p style={styles.predictTitle}>🎯 다음 훈련 집중 항목</p>
          <p style={styles.predictFocus}>{predict.focus}</p>
          <p style={styles.predictSub}>
            신뢰도 {predict.confidence}% · 누적 {predict.session_count}회 훈련
            기반
          </p>
        </div>
      )}

      {sessions.length === 0 ? (
        <p style={styles.empty}>아직 훈련 기록이 없습니다.</p>
      ) : (
        <div style={styles.grid}>
          {sessions.map((s) => (
            <div key={s.id} style={styles.card}>
              <p style={styles.date}>
                {new Date(s.created_at).toLocaleString("ko-KR")}
              </p>
              <div style={styles.row}>
                <span style={styles.label}>평균 BPM</span>
                <span style={bpmColor(s.avg_bpm)}>{s.avg_bpm?.toFixed(1)}</span>
              </div>
              <div style={styles.row}>
                <span style={styles.label}>평균 깊이</span>
                <span style={depthColor(s.avg_depth_cm)}>
                  {s.avg_depth_cm?.toFixed(1)} cm
                </span>
              </div>
              <div style={styles.row}>
                <span style={styles.label}>압박 횟수</span>
                <span style={styles.value}>{s.total_count}회</span>
              </div>
              <div style={styles.row}>
                <span style={styles.label}>자세 정확도</span>
                <span style={styles.value}>
                  {((s.posture_correct_ratio ?? 0) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function bpmColor(bpm: number): React.CSSProperties {
  return {
    color: bpm >= 100 && bpm <= 120 ? "#00e5a0" : "#ff4d4d",
    fontWeight: "bold",
  };
}

function depthColor(depth: number): React.CSSProperties {
  return {
    color: depth >= 5.0 && depth <= 6.0 ? "#00e5a0" : "#ff4d4d",
    fontWeight: "bold",
  };
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: "#0a1628",
    minHeight: "100vh",
    padding: "32px",
    color: "#fff",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "24px",
  },
  title: { color: "#00e5a0", margin: 0 },
  logoutBtn: {
    padding: "8px 16px",
    backgroundColor: "transparent",
    border: "1px solid #ff4d4d",
    color: "#ff4d4d",
    borderRadius: "8px",
    cursor: "pointer",
  },
  empty: { color: "#aaaaaa", textAlign: "center", marginTop: "80px" },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: "16px",
  },
  card: {
    backgroundColor: "#0d2137",
    borderRadius: "12px",
    padding: "20px",
    border: "1px solid #1a3a5c",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  date: { color: "#aaaaaa", fontSize: "12px", margin: 0 },
  row: { display: "flex", justifyContent: "space-between" },
  label: { color: "#aaaaaa", fontSize: "14px" },
  value: { color: "#ffffff", fontWeight: "bold" },
  predictCard: {
    backgroundColor: "#0d2137",
    borderRadius: "12px",
    padding: "24px",
    border: "1px solid #00e5a0",
    marginBottom: "24px",
    textAlign: "center" as const,
  },
  predictTitle: { color: "#aaaaaa", fontSize: "13px", margin: "0 0 8px 0" },
  predictFocus: {
    color: "#00e5a0",
    fontSize: "22px",
    fontWeight: "bold",
    margin: "0 0 8px 0",
  },
  predictSub: { color: "#aaaaaa", fontSize: "12px", margin: 0 },
};
