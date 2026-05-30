import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import apiClient from "../api/client";

export default function LoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
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
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>CPR 훈련 시스템</h2>
        <h3 style={styles.subtitle}>로그인</h3>

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
          onKeyDown={(e) => e.key === "Enter" && handleLogin()}
        />

        {error && <p style={styles.error}>{error}</p>}

        <button style={styles.button} onClick={handleLogin}>
          로그인
        </button>

        <p style={styles.link}>
          계정이 없으신가요? <Link to="/register">회원가입</Link>
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
  title: {
    color: "#00e5a0",
    textAlign: "center",
    margin: 0,
    fontSize: "20px",
  },
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
  error: {
    color: "#ff4d4d",
    fontSize: "13px",
    margin: 0,
  },
  link: {
    color: "#aaaaaa",
    textAlign: "center",
    fontSize: "13px",
  },
};
