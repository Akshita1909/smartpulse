import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer
} from "recharts";

const API = "https://smartpulse-rrr3.onrender.com";
const COLORS = ["#58a6ff", "#a371f7", "#3fb950", "#f78166", "#d29922", "#79c0ff"];

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const [dragOver, setDragOver] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post(`${API}/analyze`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResult(res.data);
      setActiveTab("overview");
    } catch (err) {
      setError("Something went wrong. Make sure your CSV has headers and valid data.");
    }
    setLoading(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.name.endsWith(".csv")) setFile(dropped);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>SmartPulse</h1>
        <p style={styles.subtitle}>
          Upload any sales CSV — get instant KPIs, charts, and AI business insights.
        </p>
      </div>

      {!result && (
        <div style={styles.uploadSection}>
          <div
            style={{ ...styles.dropzone, borderColor: dragOver ? "#58a6ff" : "#30363d" }}
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
          >
            <p style={styles.dropText}>
              {file ? `Selected: ${file.name}` : "Drag and drop your CSV here"}
            </p>
            <p style={styles.dropSubtext}>or</p>
            <label style={styles.fileLabel}>
              Browse File
              <input
                type="file"
                accept=".csv"
                style={{ display: "none" }}
                onChange={(e) => setFile(e.target.files[0])}
              />
            </label>
          </div>

          <div style={styles.sampleNote}>
            <p style={{ color: "#8b949e", fontSize: "13px", textAlign: "center" }}>
              Works with any CSV containing sales, orders, or transaction data.
              No fixed format required — AI detects your columns automatically.
            </p>
          </div>

          <button
            style={{ ...styles.button, opacity: file ? 1 : 0.5 }}
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? "Analyzing your data..." : "Generate Dashboard →"}
          </button>

          {error && <p style={styles.error}>{error}</p>}

          {loading && (
            <div style={styles.loadingBox}>
              <div style={styles.spinner} />
              <p style={styles.loadingText}>Reading CSV, detecting columns, computing metrics, generating AI insights...</p>
            </div>
          )}
        </div>
      )}

      {result && (
        <div>
          <div style={styles.resultHeader}>
            <div>
              <p style={styles.fileInfo}>{file.name} — {result.rows.toLocaleString()} rows analyzed</p>
              <p style={styles.colsDetected}>
                Detected: {Object.entries(result.columns_detected)
                  .filter(([, v]) => v)
                  .map(([k, v]) => `${k.replace("_col", "")}: "${v}"`)
                  .join(" · ")}
              </p>
            </div>
            <button style={styles.resetBtn} onClick={() => { setResult(null); setFile(null); }}>
              Upload New File
            </button>
          </div>

          {/* KPI Cards */}
          <div style={styles.metricsRow}>
            {result.metrics.total_revenue !== undefined && (
              <MetricCard title="Total Revenue" value={`$${result.metrics.total_revenue.toLocaleString()}`} />
            )}
            {result.metrics.total_profit !== undefined && (
              <MetricCard title="Total Profit" value={`$${result.metrics.total_profit.toLocaleString()}`} />
            )}
            {result.metrics.profit_margin !== undefined && (
              <MetricCard title="Profit Margin" value={`${result.metrics.profit_margin}%`} />
            )}
            <MetricCard title="Total Orders" value={result.metrics.total_orders.toLocaleString()} />
            {result.metrics.avg_order_value !== undefined && (
              <MetricCard title="Avg Order Value" value={`$${result.metrics.avg_order_value.toLocaleString()}`} />
            )}
            {result.metrics.total_quantity !== undefined && (
              <MetricCard title="Items Sold" value={result.metrics.total_quantity.toLocaleString()} />
            )}
          </div>

          {/* Tabs */}
          <div style={styles.tabRow}>
            {["overview", "geography", "insights"].map(tab => (
              <button
                key={tab}
                style={activeTab === tab ? styles.tabActive : styles.tab}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {activeTab === "overview" && (
            <div style={styles.chartsGrid}>
              {result.charts.revenue_by_category && (
                <div style={styles.chartBox}>
                  <h3 style={styles.chartTitle}>Revenue by Category</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={result.charts.revenue_by_category}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                      <XAxis dataKey="category" tick={{ fill: "#8b949e", fontSize: 11 }} />
                      <YAxis tick={{ fill: "#8b949e", fontSize: 11 }} />
                      <Tooltip contentStyle={{ backgroundColor: "#161b22", border: "1px solid #30363d" }} />
                      <Bar dataKey="revenue" fill="#58a6ff" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {result.charts.revenue_over_time && (
                <div style={styles.chartBox}>
                  <h3 style={styles.chartTitle}>Revenue Over Time</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={result.charts.revenue_over_time}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                      <XAxis dataKey="date" tick={{ fill: "#8b949e", fontSize: 10 }} />
                      <YAxis tick={{ fill: "#8b949e", fontSize: 11 }} />
                      <Tooltip contentStyle={{ backgroundColor: "#161b22", border: "1px solid #30363d" }} />
                      <Line type="monotone" dataKey="revenue" stroke="#a371f7" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {result.charts.revenue_by_segment && (
                <div style={styles.chartBox}>
                  <h3 style={styles.chartTitle}>Revenue by Segment</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie data={result.charts.revenue_by_segment} dataKey="revenue" nameKey="segment"
                        cx="50%" cy="50%" outerRadius={90}
                        label={({ segment, percent }) => `${segment} ${(percent * 100).toFixed(0)}%`}>
                        {result.charts.revenue_by_segment.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: "#161b22", border: "1px solid #30363d" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {activeTab === "geography" && (
            <div style={styles.chartsGrid}>
              {result.charts.revenue_by_region && (
                <div style={styles.chartBox}>
                  <h3 style={styles.chartTitle}>Revenue by Region</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={result.charts.revenue_by_region} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                      <XAxis type="number" tick={{ fill: "#8b949e", fontSize: 11 }} />
                      <YAxis dataKey="region" type="category" tick={{ fill: "#8b949e", fontSize: 11 }} width={100} />
                      <Tooltip contentStyle={{ backgroundColor: "#161b22", border: "1px solid #30363d" }} />
                      <Bar dataKey="revenue" fill="#3fb950" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {activeTab === "insights" && (
            <div style={styles.insightsBox}>
              <h3 style={styles.chartTitle}>AI Business Insights</h3>
              <div style={styles.insightsContent}>
                <ReactMarkdown>{result.insights}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div style={styles.metricCard}>
      <p style={styles.metricTitle}>{title}</p>
      <p style={styles.metricValue}>{value}</p>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#0d1117",
    color: "#e6edf3",
    fontFamily: "'Segoe UI', sans-serif",
    padding: "40px 20px",
    maxWidth: "1100px",
    margin: "0 auto",
  },
  header: {
    textAlign: "center",
    marginBottom: "40px",
  },
  title: {
    fontSize: "48px",
    fontWeight: "800",
    background: "linear-gradient(90deg, #58a6ff, #a371f7)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    marginBottom: "12px",
  },
  subtitle: {
    color: "#8b949e",
    fontSize: "17px",
    lineHeight: "1.6",
  },
  uploadSection: {
    maxWidth: "600px",
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "16px",
  },
  dropzone: {
    width: "100%",
    border: "2px dashed #30363d",
    borderRadius: "16px",
    padding: "60px 40px",
    textAlign: "center",
    cursor: "pointer",
    transition: "border-color 0.2s",
    backgroundColor: "#161b22",
  },
  dropText: {
    fontSize: "16px",
    color: "#e6edf3",
    marginBottom: "8px",
  },
  dropSubtext: {
    color: "#8b949e",
    fontSize: "13px",
    marginBottom: "16px",
  },
  fileLabel: {
    padding: "10px 24px",
    borderRadius: "8px",
    border: "1px solid #30363d",
    backgroundColor: "#21262d",
    color: "#e6edf3",
    cursor: "pointer",
    fontSize: "14px",
  },
  sampleNote: {
    width: "100%",
  },
  button: {
    padding: "14px 32px",
    borderRadius: "10px",
    border: "none",
    background: "linear-gradient(90deg, #58a6ff, #a371f7)",
    color: "#fff",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    width: "100%",
  },
  error: {
    color: "#f85149",
    fontSize: "14px",
  },
  loadingBox: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "16px",
    marginTop: "20px",
  },
  spinner: {
    width: "40px",
    height: "40px",
    border: "4px solid #30363d",
    borderTop: "4px solid #58a6ff",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  },
  loadingText: {
    color: "#8b949e",
    fontSize: "14px",
    textAlign: "center",
  },
  resultHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "24px",
    padding: "16px 20px",
    backgroundColor: "#161b22",
    borderRadius: "12px",
    border: "1px solid #30363d",
  },
  fileInfo: {
    fontSize: "15px",
    fontWeight: "600",
    marginBottom: "6px",
  },
  colsDetected: {
    fontSize: "12px",
    color: "#58a6ff",
  },
  resetBtn: {
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid #30363d",
    backgroundColor: "#21262d",
    color: "#e6edf3",
    cursor: "pointer",
    fontSize: "13px",
    whiteSpace: "nowrap",
  },
  metricsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
    gap: "16px",
    marginBottom: "24px",
  },
  metricCard: {
    backgroundColor: "#161b22",
    border: "1px solid #30363d",
    borderRadius: "12px",
    padding: "20px",
    textAlign: "center",
  },
  metricTitle: {
    color: "#8b949e",
    fontSize: "12px",
    marginBottom: "8px",
  },
  metricValue: {
    fontSize: "22px",
    fontWeight: "700",
    color: "#58a6ff",
  },
  tabRow: {
    display: "flex",
    gap: "8px",
    marginBottom: "24px",
  },
  tab: {
    padding: "10px 24px",
    borderRadius: "8px",
    border: "1px solid #30363d",
    backgroundColor: "#161b22",
    color: "#8b949e",
    cursor: "pointer",
    fontSize: "14px",
  },
  tabActive: {
    padding: "10px 24px",
    borderRadius: "8px",
    border: "none",
    background: "linear-gradient(90deg, #58a6ff, #a371f7)",
    color: "#fff",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "700",
  },
  chartsGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
  },
  chartBox: {
    backgroundColor: "#161b22",
    border: "1px solid #30363d",
    borderRadius: "12px",
    padding: "20px",
  },
  chartTitle: {
    fontSize: "15px",
    fontWeight: "600",
    marginBottom: "16px",
    color: "#e6edf3",
  },
  insightsBox: {
    backgroundColor: "#161b22",
    border: "1px solid #30363d",
    borderRadius: "12px",
    padding: "24px",
  },
  insightsContent: {
    lineHeight: "1.8",
    color: "#c9d1d9",
    fontSize: "14px",
  },
};