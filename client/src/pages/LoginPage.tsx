import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../api/client";

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      setError("아이디와 비밀번호를 입력해주세요.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const res = await apiClient.post("/users/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("username", username);
      navigate("/dashboard");
    } catch {
      setError("아이디 또는 비밀번호가 틀렸습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={s.page}>
      {/* 왼쪽 패널 */}
      <div style={s.leftPanel}>
        <div style={s.leftInner}>
          <div style={s.badge}>
            <span style={s.badgeDot} />
            <span style={s.badgeText}>CPR Training System</span>
          </div>
          <h1 style={s.heroTitle}>
            실시간 CPR 훈련
            <br />
            <span style={s.gradientText}>피드백 시스템</span>
          </h1>
          <p style={s.heroSub}>
            AHA 2020 가이드라인 기반 AI 분석으로
            <br />
            개인화된 CPR 훈련 피드백을 제공합니다.
          </p>
          <div style={s.featureList}>
            {[
              "실시간 압박 깊이 · 속도 측정",
              "MediaPipe 팔꿈치 자세 분석",
              "세션 기반 개인화 AI 리포트",
            ].map((f, i) => (
              <div key={i} style={s.featureItem}>
                <div style={s.featureDot} />
                <span style={s.featureText}>{f}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 오른쪽 폼 패널 */}
      <div style={s.rightPanel}>
        <div style={s.formCard}>
          <div style={{ marginBottom: "1.75rem" }}>
            <h2 style={s.formTitle}>로그인</h2>
            <p style={s.formSub}>계속하려면 로그인해주세요.</p>
          </div>

          <div style={s.fieldGroup}>
            <label style={s.label}>아이디</label>
            <input
              style={s.input}
              placeholder="아이디 입력"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            />
          </div>

          <div style={s.fieldGroup}>
            <label style={s.label}>비밀번호</label>
            <input
              style={s.input}
              placeholder="비밀번호 입력"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            />
          </div>

          {error && <p style={s.errorMsg}>{error}</p>}

          <button
            style={{ ...s.submitBtn, opacity: loading ? 0.7 : 1 }}
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? "로그인 중..." : "로그인"}
          </button>

          <p style={s.switchText}>
            계정이 없으신가요?{" "}
            <Link to="/register" style={s.switchLink}>
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  page: {
    display: "flex",
    minHeight: "100vh",
    fontFamily: "'Inter', system-ui, sans-serif",
    background: "#FAFAFA",
  },
  // 왼쪽 패널
  leftPanel: {
    flex: "1.1",
    background: "#0F172A",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "3rem",
    position: "relative",
    overflow: "hidden",
  },
  leftInner: {
    maxWidth: 420,
    position: "relative",
    zIndex: 1,
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    border: "1px solid rgba(0,82,255,0.4)",
    background: "rgba(0,82,255,0.1)",
    borderRadius: 9999,
    padding: "5px 14px",
    marginBottom: 24,
  },
  badgeDot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "#0052FF",
    display: "inline-block",
    animation: "pulse 2s infinite",
  },
  badgeText: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11,
    letterSpacing: "0.15em",
    textTransform: "uppercase" as const,
    color: "#4D7CFF",
  },
  heroTitle: {
    fontSize: "2.5rem",
    fontWeight: 700,
    color: "#fff",
    lineHeight: 1.2,
    letterSpacing: "-0.02em",
    marginBottom: 16,
  },
  gradientText: {
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  },
  heroSub: {
    fontSize: 15,
    color: "rgba(255,255,255,0.5)",
    lineHeight: 1.7,
    marginBottom: 32,
  },
  featureList: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
  },
  featureItem: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  featureDot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    flexShrink: 0,
  },
  featureText: {
    fontSize: 14,
    color: "rgba(255,255,255,0.65)",
  },
  // 오른쪽 패널
  rightPanel: {
    flex: "0.9",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "3rem",
    background: "#FAFAFA",
  },
  formCard: {
    width: "100%",
    maxWidth: 380,
  },
  formTitle: {
    fontSize: "1.75rem",
    fontWeight: 700,
    color: "#0F172A",
    letterSpacing: "-0.02em",
    marginBottom: 6,
  },
  formSub: {
    fontSize: 14,
    color: "#64748B",
  },
  fieldGroup: {
    marginBottom: "1.25rem",
  },
  label: {
    display: "block",
    fontSize: 13,
    fontWeight: 500,
    color: "#374151",
    marginBottom: 6,
  },
  input: {
    width: "100%",
    height: 48,
    padding: "0 14px",
    fontSize: 14,
    color: "#0F172A",
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 10,
    outline: "none",
    boxSizing: "border-box" as const,
    transition: "border-color 0.2s",
  },
  errorMsg: {
    fontSize: 13,
    color: "#D85A30",
    background: "rgba(216,90,48,0.06)",
    border: "1px solid rgba(216,90,48,0.2)",
    borderRadius: 8,
    padding: "10px 14px",
    marginBottom: "1rem",
  },
  submitBtn: {
    width: "100%",
    height: 48,
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    color: "#fff",
    fontSize: 15,
    fontWeight: 600,
    border: "none",
    borderRadius: 10,
    cursor: "pointer",
    transition: "all 0.2s",
    marginBottom: "1.25rem",
    letterSpacing: "-0.01em",
  },
  switchText: {
    fontSize: 13,
    color: "#64748B",
    textAlign: "center" as const,
  },
  switchLink: {
    color: "#0052FF",
    fontWeight: 500,
    textDecoration: "none",
  },
};
