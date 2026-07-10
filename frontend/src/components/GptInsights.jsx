import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { 
  FileText, 
  MessageSquare, 
  TrendingUp, 
  Activity, 
  ThumbsUp, 
  Clock, 
  AlertTriangle 
} from 'lucide-react';

const COLORS = ['#10b981', '#ef4444', '#6b7280']; // Emerald (thumbs_up), Red (thumbs_down), Gray (neutral)

export default function GptInsights({ data }) {
  if (!data) return <div className="loading-text">No data available</div>;

  const { metrics, charts } = data;

  // Defensive check: ensure GPT data keys are available before rendering
  if (!charts || !charts.daily_uploads) {
    return <div className="loading-text">Loading GPT insights...</div>;
  }

  // Custom tooltips for Recharts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{label}</p>
          {payload.map((pld, idx) => (
            <p key={idx} style={{ color: pld.color || pld.fill }}>
              {pld.name}: {pld.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="insights-container">
      {/* Metric Cards Grid */}
      <div className="metrics-grid">
        <div className="metric-card glass">
          <div className="card-header">
            <span className="card-title">GPT Health Score</span>
            <Activity className="icon text-primary" size={20} />
          </div>
          <div className="card-body">
            <span className="value">{metrics.health_score}%</span>
            <span className="subtext">Weighted performance & feedback</span>
          </div>
        </div>

        <div className="metric-card glass">
          <div className="card-header">
            <span className="card-title">Active Chat Sessions</span>
            <MessageSquare className="icon text-emerald" size={20} />
          </div>
          <div className="card-body">
            <span className="value">{metrics.active_sessions}</span>
            <span className="subtext">Across all user roles</span>
          </div>
        </div>

        <div className="metric-card glass">
          <div className="card-header">
            <span className="card-title">Total PDF Uploads</span>
            <FileText className="icon text-purple" size={20} />
          </div>
          <div className="card-body">
            <span className="value">{metrics.total_uploads}</span>
            <span className="subtext">Documents processed for GPT</span>
          </div>
        </div>

        <div className="metric-card glass">
          <div className="card-header">
            <span className="card-title">Ingestion Completion</span>
            <TrendingUp className="icon text-orange" size={20} />
          </div>
          <div className="card-body">
            <span className="value">{metrics.completion_rate}%</span>
            <span className="subtext">Successfully processed documents</span>
          </div>
        </div>

        <div className="metric-card glass">
          <div className="card-header">
            <span className="card-title">Time to First Token (TTFT)</span>
            <Clock className="icon text-blue" size={20} />
          </div>
          <div className="card-body">
            <span className="value">{metrics.avg_start_token_time_ms} ms</span>
            <span className="subtext">Prompt enter to first word response</span>
          </div>
        </div>

        <div className="metric-card glass">
          <div className="card-header">
            <span className="card-title">Total Generation Time</span>
            <Clock className="icon text-purple" size={20} />
          </div>
          <div className="card-body">
            <span className="value">{metrics.avg_last_token_time_ms} ms</span>
            <span className="subtext">Prompt enter to last word response</span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Daily Uploads Trend */}
        <div className="chart-card glass span-2">
          <h3>Daily Upload Volume</h3>
          <p className="chart-subtitle">Trend of document uploads for GPT module over the last 30 days</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={charts.daily_uploads}>
                <defs>
                  <linearGradient id="colorUploads" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                <YAxis stroke="#9ca3af" tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="uploads" name="Uploads" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorUploads)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Feedback Distribution */}
        <div className="chart-card glass">
          <h3>Feedback Distribution</h3>
          <p className="chart-subtitle">Thumbs rating on GPT assistant answers</p>
          <div className="chart-wrapper pie-wrapper">
            <ResponsiveContainer width="100%" height={230}>
              <PieChart>
                <Pie
                  data={charts.feedback_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {charts.feedback_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Message Volume Stacked Bar */}
        <div className="chart-card glass span-2">
          <h3>Message Volume by Role</h3>
          <p className="chart-subtitle">Daily count of user inquiries vs assistant responses</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.message_volume}>
                <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                <YAxis stroke="#9ca3af" tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={false} />
                <Legend iconType="circle" />
                <Bar dataKey="user" name="User Messages" stackId="a" fill="#3b82f6" radius={[0, 0, 0, 0]} />
                <Bar dataKey="assistant" name="Assistant Responses" stackId="a" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Most Used Profiles */}
        <div className="chart-card glass">
          <h3>Most Used Profiles</h3>
          <p className="chart-subtitle">PDF upload volume categorized by profiles</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.most_used_profiles} layout="vertical">
                <XAxis type="number" stroke="#9ca3af" tickLine={false} />
                <YAxis dataKey="profile" type="category" stroke="#9ca3af" tickLine={false} width={110} />
                <Tooltip content={<CustomTooltip />} cursor={false} />
                <Bar dataKey="count" name="Uploads" fill="#ec4899" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Response Time Distribution */}
        <div className="chart-card glass span-2">
          <h3>Response Time Distribution</h3>
          <p className="chart-subtitle">Frequency of chat responses within latency buckets</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={charts.response_time_distribution}>
                <XAxis dataKey="bucket" stroke="#9ca3af" tickLine={false} />
                <YAxis stroke="#9ca3af" tickLine={false} />
                <Tooltip content={<CustomTooltip />} cursor={false} />
                <Bar dataKey="count" name="Responses" fill="#f59e0b" radius={[4, 4, 0, 0]} barSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Silent Failure Rate */}
        <div className="chart-card glass">
          <h3>Silent Failure Rate</h3>
          <p className="chart-subtitle">% of slow, unrated queries (&gt;90th pct response time with neutral rating)</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={charts.silent_failures}>
                <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                <YAxis stroke="#9ca3af" tickLine={false} unit="%" />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="rate" name="Silent Failures" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* Latency Performance Trend */}
        <div className="chart-card glass span-3">
          <h3>Latency Performance Trend</h3>
          <p className="chart-subtitle">Daily average comparison of Time to First Token (TTFT) vs Total Generation Time (in ms)</p>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={charts.latency_trend}>
                <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                <YAxis stroke="#9ca3af" tickLine={false} unit=" ms" />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="circle" />
                <Line type="monotone" dataKey="avg_ttft" name="Time to First Token (TTFT)" stroke="#3b82f6" strokeWidth={2} dot={{ r: 2 }} activeDot={{ r: 4 }} />
                <Line type="monotone" dataKey="avg_total_time" name="Total Generation Time" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 2 }} activeDot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
