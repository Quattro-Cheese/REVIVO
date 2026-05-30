import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../api/client";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!username || !password) {
      setIsError(true);
      setMessage("아이디와 비밀번호를 입력해주세요.");
      return;
    }
    if (password !== confirm) {
      setIsError(true);
      setMessage("비밀번호가 일치하지 않습니다.");
      return;
    }
    setLoading(true);
    setIsError(false);
    setMessage("");
    try {
      await apiClient.post(
        `/users/register?username=${username}&password=${password}`,
      );
      setIsError(false);
      setMessage("회원가입이 완료됐습니다. 로그인 페이지로 이동합니다.");
      setTimeout(() => navigate("/login"), 1500);
    } catch {
      setIsError(true);
      setMessage("이미 존재하는 아이디입니다.");
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
            지금 시작하세요
            <br />
            <span style={s.gradientText}>무료로 가입</span>
          </h1>
          <p style={s.heroSub}>
            회원가입 후 즉시 CPR 훈련을 시작하고
            <br />
            개인화된 AI 피드백을 받아보세요.
          </p>
          <div style={s.stepList}>
            {[
              { step: "01", text: "계정 생성" },
              { step: "02", text: "CPR 훈련 시작" },
              { step: "03", text: "AI 분석 리포트 확인" },
            ].map((item) => (
              <div key={item.step} style={s.stepItem}>
                <div style={s.stepNum}>{item.step}</div>
                <span style={s.stepText}>{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 오른쪽 폼 패널 */}
      <div style={s.rightPanel}>
        <div style={s.formCard}>
          <div style={{ marginBottom: "1.75rem" }}>
            <h2 style={s.formTitle}>회원가입</h2>
            <p style={s.formSub}>아래 정보를 입력해주세요.</p>
          </div>

          <div style={s.fieldGroup}>
            <label style={s.label}>아이디</label>
            <input
              style={s.input}
              placeholder="아이디 입력"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
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
            />
          </div>

          <div style={s.fieldGroup}>
            <label style={s.label}>비밀번호 확인</label>
            <input
              style={s.input}
              placeholder="비밀번호 재입력"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRegister()}
            />
          </div>

          {message && (
            <p
              style={{
                ...s.msgBox,
                color: isError ? "#D85A30" : "#0052FF",
                background: isError
                  ? "rgba(216,90,48,0.06)"
                  : "rgba(0,82,255,0.06)",
                border: `1px solid ${isError ? "rgba(216,90,48,0.2)" : "rgba(0,82,255,0.2)"}`,
              }}
            >
              {message}
            </p>
          )}

          <button
            style={{ ...s.submitBtn, opacity: loading ? 0.7 : 1 }}
            onClick={handleRegister}
            disabled={loading}
          >
            {loading ? "처리 중..." : "회원가입"}
          </button>

          <p style={s.switchText}>
            이미 계정이 있으신가요?{" "}
            <Link to="/login" style={s.switchLink}>
              로그인
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
  stepList: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 16,
  },
  stepItem: {
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  stepNum: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11,
    fontWeight: 500,
    color: "#4D7CFF",
    background: "rgba(0,82,255,0.12)",
    border: "1px solid rgba(0,82,255,0.25)",
    borderRadius: 6,
    padding: "4px 8px",
    flexShrink: 0,
  },
  stepText: {
    fontSize: 14,
    color: "rgba(255,255,255,0.65)",
  },
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
  },
  msgBox: {
    fontSize: 13,
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
