import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../api/client";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async () => {
    try {
      await apiClient.post(
        `/users/register?username=${username}&password=${password}`,
      );
      setMessage("회원가입 완료! 로그인 해주세요.");
      setTimeout(() => navigate("/login"), 1500);
    } catch {
      setMessage("이미 존재하는 아이디입니다.");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>CPR 훈련 시스템</h2>
        <h3 style={styles.subtitle}>회원가입</h3>

        <input
          style={styles.input}
          placeholder="아이디"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          style={styles.input}
          placeholder="비밀번호"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {message && <p style={styles.message}>{message}</p>}

        <button style={styles.button} onClick={handleRegister}>
          회원가입
        </button>

        <p style={styles.link}>
          이미 계정이 있으신가요? <Link to="/login">로그인</Link>
        </p>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#0a1628",
  },
  card: {
    backgroundColor: "#0d2137",
    padding: "40px",
    borderRadius: "12px",
    width: "360px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    border: "1px solid #1a3a5c",
  },
  title: { color: "#00e5a0", textAlign: "center", margin: 0, fontSize: "20px" },
  subtitle: {
    color: "#ffffff",
    textAlign: "center",
    margin: 0,
    fontSize: "16px",
  },
  input: {
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #1a3a5c",
    backgroundColor: "#0a1628",
    color: "#ffffff",
    fontSize: "14px",
  },
  button: {
    padding: "12px",
    borderRadius: "8px",
    backgroundColor: "#00e5a0",
    color: "#0a1628",
    fontWeight: "bold",
    fontSize: "15px",
    border: "none",
    cursor: "pointer",
  },
  message: { color: "#00e5a0", fontSize: "13px", margin: 0 },
  link: { color: "#aaaaaa", textAlign: "center", fontSize: "13px" },
};
