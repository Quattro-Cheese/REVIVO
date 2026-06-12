import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
} from "recharts";
import apiClient from "../api/client";
import { useCurrentUser } from "../hooks/useCurrentUser";

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

interface ReportData {
  focus: string;
  trend: string;
  guideline: string[];
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, loading: userLoading } = useCurrentUser();
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [predict, setPredict] = useState<PredictData | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);

  useEffect(() => {
    if (!user) return; // user 로드 전엔 호출 안 함
    apiClient.get(`/sessions/${user.id}`).then((res) => setSessions(res.data));
    apiClient
      .get(`/predict/${user.id}`)
      .then((res) => setPredict(res.data))
      .catch(() => {});
    apiClient
      .get(`/report/${user.id}`)
      .then((res) => setReport(res.data))
      .catch(() => {});
  }, [user]); // user 바뀔 때마다 재호출

  // 로딩 중 화면
  if (userLoading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          background: "#FAFAFA",
        }}
      >
        <p style={{ color: "#64748B", fontSize: 14 }}>불러오는 중...</p>
      </div>
    );
  }

  // user 없으면 로그인으로
  if (!user) {
    navigate("/login");
    return null;
  }

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  };

  const handleDeleteSession = async (
    e: React.MouseEvent,
    sessionId: number,
  ) => {
    e.stopPropagation();
    if (!confirm("이 훈련 기록을 삭제하시겠습니까?")) return;
    await apiClient.delete(`/sessions/${sessionId}`);
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
  };

  // 차트 데이터 변환
  const bpmChartData = sessions.map((s, i) => ({
    name: `세션 ${i + 1}`,
    bpm: s.avg_bpm ? Math.round(s.avg_bpm * 10) / 10 : null,
  }));

  const depthChartData = sessions.map((s, i) => ({
    name: `세션 ${i + 1}`,
    depth: s.avg_depth_cm ? Math.round(s.avg_depth_cm * 10) / 10 : null,
  }));

  // 레이더 차트 데이터
  const latest = sessions[0];
  const radarData = latest
    ? [
        { subject: "압박 속도", score: bpmScore(latest.avg_bpm), full: 100 },
        {
          subject: "압박 깊이",
          score: depthScore(latest.avg_depth_cm),
          full: 100,
        },
        {
          subject: "팔꿈치 자세",
          score: Math.round((latest.posture_correct_ratio ?? 0) * 100),
          full: 100,
        },
        { subject: "일관성", score: 78, full: 100 },
        {
          subject: "압박 횟수",
          score: Math.min(100, Math.round((latest.total_count / 30) * 100)),
          full: 100,
        },
      ]
    : [];

  return (
    <div style={s.page}>
      {/* 헤더 */}
      <div style={s.header}>
        <div>
          <div style={s.badge}>
            <span style={s.badgeDot} />
            <span style={s.badgeText}>CPR Training</span>
          </div>
          <h1 style={s.pageTitle}>
            {user.username}님의{" "}
            <span style={s.gradientText}>훈련 대시보드</span>
          </h1>
          <p style={s.pageSub}>
            누적 {sessions.length}회 훈련
            {latest &&
              ` · 마지막 훈련 ${new Date(latest.created_at).toLocaleDateString("ko-KR")}`}
          </p>
        </div>
        <button style={s.logoutBtn} onClick={handleLogout}>
          로그아웃
        </button>
      </div>

      {/* 지표 카드 4개 */}
      {latest && (
        <div style={s.metricRow}>
          <MetricCard
            label="평균 BPM"
            value={latest.avg_bpm?.toFixed(1)}
            good={latest.avg_bpm >= 100 && latest.avg_bpm <= 120}
            badge={
              latest.avg_bpm >= 100 && latest.avg_bpm <= 120
                ? "목표 범위 내"
                : "범위 벗어남"
            }
          />
          <MetricCard
            label="평균 압박 깊이"
            value={`${latest.avg_depth_cm?.toFixed(1)} cm`}
            good={latest.avg_depth_cm >= 5 && latest.avg_depth_cm <= 6}
            badge={
              latest.avg_depth_cm >= 5 && latest.avg_depth_cm <= 6
                ? "적정 범위"
                : "범위 벗어남"
            }
          />
          <MetricCard
            label="총 압박 횟수"
            value={`${latest.total_count}회`}
            good={true}
            badge="세션 완료"
          />
          <MetricCard
            label="자세 정확도"
            value={`${Math.round((latest.posture_correct_ratio ?? 0) * 100)}%`}
            good={(latest.posture_correct_ratio ?? 0) >= 0.8}
            badge={
              (latest.posture_correct_ratio ?? 0) >= 0.8 ? "양호" : "개선 필요"
            }
          />
        </div>
      )}

      {/* AI 예측 카드 */}
      {predict && (
        <div style={s.predictCard}>
          <div>
            <p style={s.predictLabel}>AI 분석 · 다음 훈련 집중 항목</p>
            <p style={s.predictFocus}>{predict.focus}</p>
            <p style={s.predictConf}>
              신뢰도 {predict.confidence}% · {predict.session_count}회 훈련 기반
              분석
            </p>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={s.predictScore}>{predict.confidence}</div>
            <div style={s.predictScoreLabel}>신뢰도 점수</div>
          </div>
        </div>
      )}

      {/* 차트 그리드 */}
      {sessions.length > 0 && (
        <div style={s.chartsGrid}>
          {/* BPM 라인 차트 */}
          <div style={s.chartCard}>
            <p style={s.chartTitle}>BPM 추이</p>
            <p style={s.chartSub}>세션별 평균 압박 속도</p>
            <ChartLegend
              items={[
                { color: "#0052FF", label: "실제 BPM" },
                {
                  color: "#CBD5E1",
                  label: "목표 범위 (100~120)",
                  dashed: true,
                },
              ]}
            />
            <ResponsiveContainer width="100%" height={180}>
              <LineChart
                data={bpmChartData}
                margin={{ top: 8, right: 16, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                />
                <YAxis
                  domain={[80, 140]}
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <ReferenceArea y1={100} y2={120} fill="rgba(0,82,255,0.05)" />
                <ReferenceLine y={100} stroke="#CBD5E1" strokeDasharray="4 4" />
                <ReferenceLine y={120} stroke="#CBD5E1" strokeDasharray="4 4" />
                <Line
                  type="monotone"
                  dataKey="bpm"
                  stroke="#0052FF"
                  strokeWidth={2}
                  dot={{ fill: "#0052FF", r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 깊이 라인 차트 */}
          <div style={s.chartCard}>
            <p style={s.chartTitle}>압박 깊이 추이</p>
            <p style={s.chartSub}>세션별 평균 압박 깊이 (cm)</p>
            <ChartLegend
              items={[
                { color: "#4D7CFF", label: "실제 깊이" },
                { color: "#CBD5E1", label: "목표 범위 (5~6cm)", dashed: true },
              ]}
            />
            <ResponsiveContainer width="100%" height={180}>
              <LineChart
                data={depthChartData}
                margin={{ top: 8, right: 16, left: -16, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                />
                <YAxis
                  domain={[3, 8]}
                  tick={{ fontSize: 11, fill: "#94A3B8" }}
                  tickFormatter={(v) => `${v}cm`}
                />
                <Tooltip
                  contentStyle={tooltipStyle}
                  formatter={(v) => [`${v} cm`, "깊이"]}
                />
                <ReferenceArea y1={5} y2={6} fill="rgba(77,124,255,0.06)" />
                <ReferenceLine y={5} stroke="#CBD5E1" strokeDasharray="4 4" />
                <ReferenceLine y={6} stroke="#CBD5E1" strokeDasharray="4 4" />
                <Line
                  type="monotone"
                  dataKey="depth"
                  stroke="#4D7CFF"
                  strokeWidth={2}
                  dot={{ fill: "#4D7CFF", r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 레이더 차트 */}
          {radarData.length > 0 && (
            <div style={{ ...s.chartCard, gridColumn: "1 / -1" }}>
              <p style={s.chartTitle}>종합 성과 분석</p>
              <p style={s.chartSub}>AHA 가이드라인 기준 항목별 달성도</p>
              <ChartLegend
                items={[
                  { color: "#0052FF", label: "이번 세션" },
                  { color: "#CBD5E1", label: "AHA 목표 (100%)", dashed: true },
                ]}
              />
              <ResponsiveContainer width="100%" height={280}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#F1F5F9" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fontSize: 12, fill: "#64748B" }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 100]}
                    tick={false}
                    axisLine={false}
                  />
                  <Radar
                    name="AHA 목표"
                    dataKey="full"
                    stroke="#CBD5E1"
                    fill="rgba(203,213,225,0.1)"
                    strokeDasharray="4 4"
                  />
                  <Radar
                    name="이번 세션"
                    dataKey="score"
                    stroke="#0052FF"
                    fill="rgba(0,82,255,0.12)"
                    strokeWidth={2}
                    dot={{ fill: "#0052FF", r: 4 }}
                  />
                  <Legend iconType="square" wrapperStyle={{ fontSize: 12 }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* 가이드라인 */}
      {report && report.guideline.length > 0 && (
        <div style={s.guidelineCard}>
          <p style={s.chartTitle}>📌 AHA 가이드라인 기반 피드백</p>
          {report.guideline.map((g, i) => (
            <div key={i} style={s.guidelineContent}>
              <div style={s.guidelineBar} />
              <p style={s.guidelineText}>{g}</p>
            </div>
          ))}
        </div>
      )}

      {/* 세션 목록 */}
      <div style={{ marginTop: "2rem" }}>
        <div style={s.sectionLabel}>
          훈련 기록
          <span style={s.sectionCount}>{sessions.length} sessions</span>
        </div>
        <div style={s.sessionGrid}>
          {sessions.map((session) => (
            <div
              key={session.id}
              style={s.sessionCard}
              onClick={() => navigate(`/report/${session.id}`)}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 10,
                }}
              >
                <p style={{ ...s.sessionDate, marginBottom: 0 }}>
                  {new Date(session.created_at).toLocaleString("ko-KR")}
                </p>
                <button
                  style={s.deleteBtn}
                  onClick={(e) => handleDeleteSession(e, session.id)}
                  title="기록 삭제"
                >
                  ✕
                </button>
              </div>
              <SessionRow
                label="평균 BPM"
                value={session.avg_bpm?.toFixed(1)}
                good={session.avg_bpm >= 100 && session.avg_bpm <= 120}
              />
              <SessionRow
                label="평균 깊이"
                value={`${session.avg_depth_cm?.toFixed(1)} cm`}
                good={session.avg_depth_cm >= 5 && session.avg_depth_cm <= 6}
              />
              <SessionRow
                label="압박 횟수"
                value={`${session.total_count}회`}
              />
              <SessionRow
                label="자세 정확도"
                value={`${Math.round((session.posture_correct_ratio ?? 0) * 100)}%`}
                good={(session.posture_correct_ratio ?? 0) >= 0.8}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── 서브 컴포넌트 ──────────────────────────────

function MetricCard({
  label,
  value,
  good,
  badge,
}: {
  label: string;
  value?: string;
  good?: boolean;
  badge: string;
}) {
  return (
    <div style={s.metricCard}>
      <p style={s.metricLabel}>{label}</p>
      <p style={{ ...s.metricValue, color: good ? "#0052FF" : "#D85A30" }}>
        {value}
      </p>
      <span
        style={{
          ...s.metricBadge,
          background: good ? "rgba(0,82,255,0.08)" : "rgba(216,90,48,0.08)",
          color: good ? "#0052FF" : "#D85A30",
        }}
      >
        {badge}
      </span>
    </div>
  );
}

function SessionRow({
  label,
  value,
  good,
}: {
  label: string;
  value?: string;
  good?: boolean;
}) {
  return (
    <div style={s.sessionRow}>
      <span style={s.sessionKey}>{label}</span>
      <span
        style={{
          ...s.sessionVal,
          color: good === undefined ? "#0F172A" : good ? "#0052FF" : "#D85A30",
        }}
      >
        {value}
      </span>
    </div>
  );
}

function ChartLegend({
  items,
}: {
  items: { color: string; label: string; dashed?: boolean }[];
}) {
  return (
    <div style={{ display: "flex", gap: 16, marginBottom: 12 }}>
      {items.map((item, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div
            style={{
              width: 24,
              height: 2,
              background: item.dashed ? "transparent" : item.color,
              borderTop: item.dashed ? `2px dashed ${item.color}` : "none",
            }}
          />
          <span style={{ fontSize: 12, color: "#64748B" }}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// ── 유틸 ──────────────────────────────

function bpmScore(bpm: number): number {
  if (!bpm) return 0;
  if (bpm >= 100 && bpm <= 120) return 100;
  if (bpm < 100) return Math.max(0, Math.round(100 - (100 - bpm) * 3));
  return Math.max(0, Math.round(100 - (bpm - 120) * 3));
}

function depthScore(depth: number): number {
  if (!depth) return 0;
  if (depth >= 5 && depth <= 6) return 100;
  if (depth < 5) return Math.max(0, Math.round(100 - (5 - depth) * 30));
  return Math.max(0, Math.round(100 - (depth - 6) * 30));
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const tooltipStyle: any = {
  background: "#fff",
  border: "1px solid #E2E8F0",
  borderRadius: 10,
  fontSize: 12,
};

// ── 스타일 ──────────────────────────────

const s: Record<string, React.CSSProperties> = {
  page: {
    background: "#FAFAFA",
    minHeight: "100vh",
    padding: "2rem",
    fontFamily: "'Inter', system-ui, sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "2rem",
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    border: "1px solid rgba(0,82,255,0.25)",
    background: "rgba(0,82,255,0.05)",
    borderRadius: 9999,
    padding: "5px 14px",
    marginBottom: 10,
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
    color: "#0052FF",
  },
  pageTitle: {
    fontSize: "1.75rem",
    fontWeight: 600,
    color: "#0F172A",
    letterSpacing: "-0.02em",
    lineHeight: 1.2,
  },
  gradientText: {
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  },
  pageSub: { fontSize: 14, color: "#64748B", marginTop: 6 },
  logoutBtn: {
    fontSize: 13,
    color: "#64748B",
    background: "transparent",
    border: "1px solid #E2E8F0",
    borderRadius: 10,
    padding: "8px 16px",
    cursor: "pointer",
  },
  metricRow: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 12,
    marginBottom: "1.5rem",
  },
  metricCard: { background: "#F1F5F9", borderRadius: 10, padding: "1rem" },
  metricLabel: { fontSize: 12, color: "#64748B", marginBottom: 6 },
  metricValue: {
    fontSize: 22,
    fontWeight: 600,
    letterSpacing: "-0.02em",
    marginBottom: 4,
  },
  metricBadge: {
    display: "inline-block",
    fontSize: 11,
    padding: "2px 8px",
    borderRadius: 9999,
  },
  predictCard: {
    background: "#0F172A",
    borderRadius: 16,
    padding: "1.5rem",
    marginBottom: "1.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  predictLabel: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11,
    letterSpacing: "0.15em",
    textTransform: "uppercase" as const,
    color: "rgba(255,255,255,0.4)",
    marginBottom: 8,
  },
  predictFocus: { fontSize: 18, fontWeight: 600, color: "#fff" },
  predictConf: { fontSize: 13, color: "rgba(255,255,255,0.5)", marginTop: 4 },
  predictScore: {
    fontSize: "3rem",
    fontWeight: 600,
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
    letterSpacing: "-0.03em",
  },
  predictScoreLabel: { fontSize: 12, color: "rgba(255,255,255,0.4)" },
  chartsGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
    marginBottom: 16,
  },
  chartCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 16,
    padding: "1.25rem",
  },
  chartTitle: {
    fontSize: 14,
    fontWeight: 500,
    color: "#0F172A",
    marginBottom: 4,
  },
  chartSub: { fontSize: 12, color: "#64748B", marginBottom: "0.75rem" },
  guidelineCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 16,
    padding: "1.25rem",
    marginBottom: 16,
  },
  guidelineContent: { display: "flex", gap: 12, marginTop: 10 },
  guidelineBar: {
    width: 3,
    background: "linear-gradient(to bottom, #0052FF, #4D7CFF)",
    borderRadius: 2,
    flexShrink: 0,
  },
  guidelineText: { fontSize: 13, color: "#475569", lineHeight: 1.7 },
  sectionLabel: {
    fontSize: 13,
    fontWeight: 500,
    color: "#0F172A",
    marginBottom: 12,
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  sectionCount: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11,
    color: "#64748B",
    background: "#F1F5F9",
    padding: "2px 8px",
    borderRadius: 6,
  },
  sessionGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    gap: 10,
  },
  sessionCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 12,
    padding: "1rem",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  sessionDate: { fontSize: 11, color: "#94A3B8", marginBottom: 10 },
  deleteBtn: {
    background: "transparent",
    border: "none",
    color: "#CBD5E1",
    fontSize: 12,
    cursor: "pointer",
    padding: "2px 4px",
    borderRadius: 4,
    lineHeight: 1,
    flexShrink: 0,
  },
  sessionRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  sessionKey: { fontSize: 12, color: "#64748B" },
  sessionVal: { fontSize: 13, fontWeight: 500 },
};
