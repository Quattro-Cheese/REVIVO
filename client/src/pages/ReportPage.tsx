import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import apiClient from "../api/client";
import { useCurrentUser } from "../hooks/useCurrentUser";

interface SessionDetail {
  id: number;
  created_at: string;
  avg_bpm: number;
  avg_depth_cm: number;
  total_count: number;
  posture_correct_ratio: number;
  duration_sec: number;
  prev_session: {
    avg_bpm: number;
    avg_depth_cm: number;
    posture_correct_ratio: number;
  } | null;
}

interface ReportData {
  focus: string;
  trend: string;
  guideline: string[];
}

interface SessionStats {
  bpm_std: number;
  depth_std: number;
  posture_std: number;
  count_std: number;
  session_count: number;
}

export default function ReportPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useCurrentUser();

  useEffect(() => {
    if (!sessionId || !user) return;
    Promise.all([
      apiClient.get(`/sessions/detail/${sessionId}`),
      apiClient.get(`/report/${user.id}`),
      apiClient.get(`/sessions/stats`),
    ])
      .then(([detailRes, reportRes, statsRes]) => {
        setDetail(detailRes.data);
        setReport(reportRes.data);
        setStats(statsRes.data);
      })
      .finally(() => setLoading(false));
  }, [sessionId, user]);

  if (loading) {
    return (
      <div style={s.loadingWrap}>
        <p style={s.loadingText}>리포트 불러오는 중...</p>
      </div>
    );
  }

  if (!detail) {
    return (
      <div style={s.loadingWrap}>
        <p style={s.loadingText}>세션을 찾을 수 없습니다.</p>
      </div>
    );
  }

  const std = stats ?? FALLBACK_STD;
  const scores = {
    bpm: calcBpmScore(detail.avg_bpm, std.bpm_std),
    depth: calcDepthScore(detail.avg_depth_cm, std.depth_std),
    posture: calcPostureScore(
      detail.posture_correct_ratio ?? 0,
      std.posture_std,
    ),
    count: calcCountScore(
      detail.total_count,
      detail.duration_sec,
      std.count_std,
    ),
  };

  const radarData = [
    { subject: "압박 속도", score: scores.bpm, full: 100 },
    { subject: "압박 깊이", score: scores.depth, full: 100 },
    { subject: "팔꿈치 자세", score: scores.posture, full: 100 },
    { subject: "압박 횟수", score: scores.count, full: 100 },
  ];

  const overallScore = Math.round(
    (WEIGHTS.bpm * scores.bpm +
      WEIGHTS.depth * scores.depth +
      WEIGHTS.posture * scores.posture +
      WEIGHTS.count * scores.count) /
      (WEIGHTS.bpm + WEIGHTS.depth + WEIGHTS.posture + WEIGHTS.count),
  );

  return (
    <div style={s.page}>
      {/* 헤더 */}
      <div style={s.header}>
        <button style={s.backBtn} onClick={() => navigate(-1)}>
          ← 대시보드로
        </button>
        <div style={s.badge}>
          <span style={s.badgeDot} />
          <span style={s.badgeText}>Session Report</span>
        </div>
      </div>

      {/* 타이틀 */}
      <div style={s.titleSection}>
        <h1 style={s.pageTitle}>
          세션 <span style={s.gradientText}>#{detail.id}</span> 리포트
        </h1>
        <p style={s.pageSub}>
          {new Date(detail.created_at).toLocaleString("ko-KR")} ·{" "}
          {Math.round(detail.duration_sec)}초 훈련
        </p>
      </div>

      {/* 종합 점수 카드 */}
      <div style={s.scoreCard}>
        <div style={s.scoreLeft}>
          <p style={s.scoreLabel}>종합 점수</p>
          <div style={s.scoreBig}>{overallScore}</div>
          <p style={s.scoreDesc}>AHA 가이드라인 기준 4개 항목 가중 평균</p>
        </div>
        <div style={s.scoreRight}>
          {report && (
            <>
              <p style={s.focusLabel}>다음 훈련 집중 항목</p>
              <p style={s.focusText}>{report.focus}</p>
              {report.trend && <p style={s.trendText}>📈 {report.trend}</p>}
            </>
          )}
        </div>
      </div>

      {/* 지표 카드 */}
      <div style={s.metricRow}>
        <MetricCard
          label="평균 BPM"
          value={detail.avg_bpm?.toFixed(1)}
          target="100~120"
          good={detail.avg_bpm >= 100 && detail.avg_bpm <= 120}
          prev={detail.prev_session?.avg_bpm?.toFixed(1)}
        />
        <MetricCard
          label="압박 깊이"
          value={`${detail.avg_depth_cm?.toFixed(1)} cm`}
          target="5~6 cm"
          good={detail.avg_depth_cm >= 5 && detail.avg_depth_cm <= 6}
          prev={
            detail.prev_session
              ? `${detail.prev_session.avg_depth_cm?.toFixed(1)} cm`
              : undefined
          }
        />
        <MetricCard
          label="압박 횟수"
          value={`${detail.total_count}회`}
          target="30회 이상"
          good={detail.total_count >= 30}
        />
        <MetricCard
          label="자세 정확도"
          value={`${Math.round((detail.posture_correct_ratio ?? 0) * 100)}%`}
          target="80% 이상"
          good={(detail.posture_correct_ratio ?? 0) >= 0.8}
          prev={
            detail.prev_session
              ? `${Math.round((detail.prev_session.posture_correct_ratio ?? 0) * 100)}%`
              : undefined
          }
        />
      </div>

      {/* 레이더 차트 */}
      <div style={s.chartCard}>
        <p style={s.chartTitle}>항목별 달성도</p>
        <p style={s.chartSub}>AHA 2020 가이드라인 기준</p>
        <ResponsiveContainer width="100%" height={300}>
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
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(v) => [`${v}점`, ""]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* 이전 세션 비교 */}
      {detail.prev_session && (
        <div style={s.compareCard}>
          <p style={s.chartTitle}>이전 세션 비교</p>
          <div style={s.compareGrid}>
            <CompareRow
              label="평균 BPM"
              current={detail.avg_bpm}
              prev={detail.prev_session.avg_bpm}
              unit=""
              good={(v) => v >= 100 && v <= 120}
            />
            <CompareRow
              label="압박 깊이"
              current={detail.avg_depth_cm}
              prev={detail.prev_session.avg_depth_cm}
              unit=" cm"
              good={(v) => v >= 5 && v <= 6}
            />
            <CompareRow
              label="자세 정확도"
              current={Math.round((detail.posture_correct_ratio ?? 0) * 100)}
              prev={Math.round(
                (detail.prev_session.posture_correct_ratio ?? 0) * 100,
              )}
              unit="%"
              good={(v) => v >= 80}
            />
          </div>
        </div>
      )}

      {/* AHA 가이드라인 */}
      {report && report.guideline.length > 0 && (
        <div style={s.guidelineCard}>
          <p style={s.chartTitle}>📌 AHA 가이드라인 기반 피드백</p>
          {report.guideline.map((g, i) => (
            <div key={i} style={s.guidelineRow}>
              <div style={s.guidelineBar} />
              <p style={s.guidelineText}>{g}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── 서브 컴포넌트 ──────────────────────────────

function MetricCard({
  label,
  value,
  target,
  good,
  prev,
}: {
  label: string;
  value?: string;
  target: string;
  good?: boolean;
  prev?: string;
}) {
  return (
    <div style={s.metricCard}>
      <p style={s.metricLabel}>{label}</p>
      <p style={{ ...s.metricValue, color: good ? "#0052FF" : "#D85A30" }}>
        {value}
      </p>
      <p style={s.metricTarget}>목표 {target}</p>
      {prev && <p style={s.metricPrev}>이전 {prev}</p>}
    </div>
  );
}

function CompareRow({
  label,
  current,
  prev,
  unit,
  good,
}: {
  label: string;
  current: number;
  prev: number;
  unit: string;
  good: (v: number) => boolean;
}) {
  const diff = current - prev;
  const improved = Math.abs(current - 110) < Math.abs(prev - 110); // 목표에 가까워졌는지
  return (
    <div style={s.compareRow}>
      <span style={s.compareLabel}>{label}</span>
      <div style={s.compareValues}>
        <span style={{ color: "#94A3B8", fontSize: 13 }}>
          {prev.toFixed(1)}
          {unit}
        </span>
        <span style={{ color: "#CBD5E1", fontSize: 12, margin: "0 8px" }}>
          →
        </span>
        <span
          style={{
            color: good(current) ? "#0052FF" : "#D85A30",
            fontWeight: 600,
            fontSize: 14,
          }}
        >
          {current.toFixed(1)}
          {unit}
        </span>
        <span
          style={{
            marginLeft: 8,
            fontSize: 12,
            color: improved ? "#0052FF" : diff === 0 ? "#94A3B8" : "#D85A30",
          }}
        >
          {diff > 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1)}
          {unit}
        </span>
      </div>
    </div>
  );
}

// ── 점수 계산 ──────────────────────────────
// score_i = max(0, 100 - w_i × |deviation_i / σ_i| × 100)
// deviation: 정답 범위(AHA 가이드라인)에서 벗어난 양 (범위 내이면 0)
// σ: 전체 세션의 해당 지표 표준편차 (단위 통일을 위한 정규화)

const WEIGHTS = { bpm: 0.3, depth: 0.4, posture: 0.25, count: 0.25 };

const FALLBACK_STD = {
  bpm_std: 15.0,
  depth_std: 1.5,
  posture_std: 0.2,
  count_std: 10.0,
};

function calcBpmScore(bpm: number, sigma: number): number {
  if (!bpm) return 0;
  const deviation = bpm < 100 ? 100 - bpm : bpm > 120 ? bpm - 120 : 0;
  return Math.max(0, Math.round(100 - WEIGHTS.bpm * (deviation / sigma) * 100));
}

function calcDepthScore(depth: number, sigma: number): number {
  if (!depth) return 0;
  const deviation = depth < 5 ? 5 - depth : depth > 6 ? depth - 6 : 0;
  return Math.max(
    0,
    Math.round(100 - WEIGHTS.depth * (deviation / sigma) * 100),
  );
}
function calcPostureScore(ratio: number, sigma: number): number {
  const deviation = 1.0 - ratio;
  return Math.max(
    0,
    Math.round(100 - WEIGHTS.posture * (deviation / sigma) * 100),
  );
}

function calcCountScore(
  count: number,
  durationSec: number,
  sigma: number,
): number {
  const target = (durationSec / 60) * 110;
  const deviation = Math.abs(count - target);
  return Math.max(
    0,
    Math.round(100 - WEIGHTS.count * (deviation / sigma) * 100),
  );
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
    maxWidth: 900,
    margin: "0 auto",
  },
  loadingWrap: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    background: "#FAFAFA",
  },
  loadingText: { color: "#64748B", fontSize: 14 },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1.5rem",
  },
  backBtn: {
    fontSize: 13,
    color: "#64748B",
    background: "transparent",
    border: "1px solid #E2E8F0",
    borderRadius: 10,
    padding: "8px 16px",
    cursor: "pointer",
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    border: "1px solid rgba(0,82,255,0.25)",
    background: "rgba(0,82,255,0.05)",
    borderRadius: 9999,
    padding: "5px 14px",
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
  titleSection: { marginBottom: "1.5rem" },
  pageTitle: {
    fontSize: "1.75rem",
    fontWeight: 600,
    color: "#0F172A",
    letterSpacing: "-0.02em",
  },
  gradientText: {
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  },
  pageSub: { fontSize: 14, color: "#64748B", marginTop: 6 },
  scoreCard: {
    background: "#0F172A",
    borderRadius: 16,
    padding: "1.5rem",
    marginBottom: "1.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  scoreLeft: {},
  scoreLabel: {
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 11,
    letterSpacing: "0.15em",
    textTransform: "uppercase" as const,
    color: "rgba(255,255,255,0.4)",
    marginBottom: 8,
  },
  scoreBig: {
    fontSize: "4rem",
    fontWeight: 700,
    background: "linear-gradient(135deg, #0052FF, #4D7CFF)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
    letterSpacing: "-0.03em",
    lineHeight: 1,
  },
  scoreDesc: { fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 8 },
  scoreRight: { textAlign: "right" as const },
  focusLabel: {
    fontSize: 11,
    color: "rgba(255,255,255,0.4)",
    marginBottom: 8,
    textTransform: "uppercase" as const,
    letterSpacing: "0.1em",
  },
  focusText: { fontSize: 18, fontWeight: 600, color: "#fff" },
  trendText: { fontSize: 13, color: "rgba(255,255,255,0.5)", marginTop: 6 },
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
  metricTarget: { fontSize: 11, color: "#94A3B8" },
  metricPrev: { fontSize: 11, color: "#94A3B8", marginTop: 2 },
  chartCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 16,
    padding: "1.25rem",
    marginBottom: 16,
  },
  chartTitle: {
    fontSize: 14,
    fontWeight: 500,
    color: "#0F172A",
    marginBottom: 4,
  },
  chartSub: { fontSize: 12, color: "#64748B", marginBottom: "0.75rem" },
  compareCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 16,
    padding: "1.25rem",
    marginBottom: 16,
  },
  compareGrid: {
    display: "flex",
    flexDirection: "column" as const,
    gap: 12,
    marginTop: 12,
  },
  compareRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 0",
    borderBottom: "1px solid #F1F5F9",
  },
  compareLabel: { fontSize: 13, color: "#64748B" },
  compareValues: { display: "flex", alignItems: "center" },
  guidelineCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 16,
    padding: "1.25rem",
  },
  guidelineRow: { display: "flex", gap: 12, marginTop: 10 },
  guidelineBar: {
    width: 3,
    minHeight: 40,
    background: "linear-gradient(to bottom, #0052FF, #4D7CFF)",
    borderRadius: 2,
    flexShrink: 0,
  },
  guidelineText: { fontSize: 13, color: "#475569", lineHeight: 1.7 },
};
