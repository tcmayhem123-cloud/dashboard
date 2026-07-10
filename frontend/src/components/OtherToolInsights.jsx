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
  Image, 
  Globe, 
  FileCheck, 
  Users, 
  CheckCircle, 
  HelpCircle,
  FileText
} from 'lucide-react';

const BUILD_COLORS = ['#10b981', '#ef4444']; // Success, Failed

export default function OtherToolInsights({ toolKey, data }) {
  if (!data) return <div className="loading-text">No data available</div>;

  const { metrics, charts } = data;

  // Defensive check: ensure the data structure matches the currently selected tool
  if (toolKey === "text_to_image" && (!charts || !charts.usage_vs_quota)) {
    return <div className="loading-text">Loading Text-to-Image insights...</div>;
  }
  if (toolKey === "translation" && (!charts || !charts.language_pairs)) {
    return <div className="loading-text">Loading Translation insights...</div>;
  }
  if (toolKey === "pdf_chat" && (!charts || !charts.build_history)) {
    return <div className="loading-text">Loading PDF Chat insights...</div>;
  }
  if (toolKey === "mom_transcription" && (!charts || !charts.pipeline_funnel)) {
    return <div className="loading-text">Loading MoM Transcription insights...</div>;
  }
  if (toolKey === "overall" && (!charts || !charts.power_users)) {
    return <div className="loading-text">Loading Platform insights...</div>;
  }

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

  if (toolKey === "text_to_image") {
    const usagePct = Math.min(100, Math.round((metrics.total_generated / (metrics.daily_limit * metrics.active_users || 1)) * 100));

    return (
      <div className="insights-container">
        <div className="metrics-grid">
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Images Generated</span>
              <Image className="icon text-primary" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.total_generated}</span>
              <span className="subtext">Accumulated total generations</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Active Creators</span>
              <Users className="icon text-emerald" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.active_users}</span>
              <span className="subtext">Unique users in last 10 days</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Quota Usage</span>
              <Globe className="icon text-orange" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{usagePct}%</span>
              <span className="subtext">Avg usage relative to limit</span>
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card glass span-2">
            <h3>Image Generation Usage vs Quota</h3>
            <p className="chart-subtitle">Daily count of images generated vs daily quota limits</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={charts.usage_vs_quota}>
                  <defs>
                    <linearGradient id="colorGen" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Area type="monotone" dataKey="generated" name="Generated Images" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorGen)" />
                  <Line type="monotone" dataKey="quota" name="Daily Limit Reference" stroke="#ef4444" strokeDasharray="5 5" dot={false} strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Resolution Distribution</h3>
            <p className="chart-subtitle">Breakdown of generated image dimensions</p>
            <div className="chart-wrapper pie-wrapper">
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={charts.resolution_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {charts.resolution_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#f59e0b', '#ec4899'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass span-3">
            <h3>Generation Configuration Trends</h3>
            <p className="chart-subtitle">Daily average of inference steps vs guidance scale values</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={charts.settings_trend}>
                  <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconType="circle" />
                  <Line type="monotone" dataKey="avg_steps" name="Inference Steps" stroke="#3b82f6" strokeWidth={2} dot={{ r: 2 }} />
                  <Line type="monotone" dataKey="avg_guidance" name="Guidance Scale" stroke="#ec4899" strokeWidth={2} dot={{ r: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (toolKey === "translation") {
    return (
      <div className="insights-container">
        <div className="metrics-grid">
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Translations Processed</span>
              <Globe className="icon text-primary" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.total_translations}</span>
              <span className="subtext">Total texts & audios translated</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Languages Supported</span>
              <Globe className="icon text-emerald" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.languages_supported}</span>
              <span className="subtext">Multi-lingual translations supported</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Voice Translations</span>
              <Globe className="icon text-purple" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.voice_translations}</span>
              <span className="subtext">Audio translations completed</span>
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card glass span-2">
            <h3>Translation Language Pairs</h3>
            <p className="chart-subtitle">Top source to target language pairs by execution frequency</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.language_pairs}>
                  <XAxis dataKey="pair" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={false} />
                  <Bar dataKey="count" name="Translations Count" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Translation Mode Breakdown</h3>
            <p className="chart-subtitle">Distribution of text translation vs audio translation</p>
            <div className="chart-wrapper pie-wrapper">
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={charts.feature_breakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {charts.feature_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#10b981', '#8b5cf6'][index % 2]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass span-3">
            <h3>Daily Translation Activity</h3>
            <p className="chart-subtitle">Trend of translation requests processed over the last 15 days</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={charts.daily_translation_trend}>
                  <defs>
                    <linearGradient id="colorTrans" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="count" name="Translations" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorTrans)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (toolKey === "pdf_chat") {
    return (
      <div className="insights-container">
        <div className="metrics-grid">
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Build Success Rate</span>
              <CheckCircle className="icon text-emerald" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.build_success_rate}%</span>
              <span className="subtext">Ratio of successful builds</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Total PDF Builds</span>
              <FileText className="icon text-primary" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.total_builds}</span>
              <span className="subtext">Document build pipelines executed</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Ingestion Quality</span>
              <FileCheck className="icon text-orange" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.avg_ingestion_completion}</span>
              <span className="subtext">Avg ratio of pages successfully indexed</span>
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card glass span-2">
            <h3>PDF Build History</h3>
            <p className="chart-subtitle">Timeline of successful vs failed document ingestion builds</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.build_history}>
                  <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={false} />
                  <Legend iconType="circle" />
                  <Bar dataKey="success" name="Successful Builds" fill="#10b981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="failed" name="Failed Builds" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Build Status Split</h3>
            <p className="chart-subtitle">Breakdown of builds success vs fail rates</p>
            <div className="chart-wrapper pie-wrapper">
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={charts.build_status_split}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {charts.build_status_split.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={BUILD_COLORS[index % BUILD_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass span-2">
            <h3>Daily Ingested Volume</h3>
            <p className="chart-subtitle">Total number of PDF document pages processed daily</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.daily_pages_processed}>
                  <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} cursor={false} />
                  <Bar dataKey="pages" name="Pages Processed" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={30} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Document Layout Categories</h3>
            <p className="chart-subtitle">Indexed PDF files grouped by document type template</p>
            <div className="chart-wrapper pie-wrapper">
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={charts.document_type_breakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={0}
                    outerRadius={75}
                    dataKey="value"
                  >
                    {charts.document_type_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#3b82f6', '#10b981', '#ec4899', '#f59e0b'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (toolKey === "mom_transcription") {
    return (
      <div className="insights-container">
        <div className="metrics-grid">
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Meetings Transcribed</span>
              <FileCheck className="icon text-primary" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.total_meetings}</span>
              <span className="subtext">Uploaded audio records</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Completed MoMs</span>
              <CheckCircle className="icon text-emerald" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.completed_moms}</span>
              <span className="subtext">Meetings with final MoM document</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Pending Stages</span>
              <HelpCircle className="icon text-orange" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.pending_moms}</span>
              <span className="subtext">Meetings awaiting completion</span>
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card glass span-2">
            <h3>Pipeline Stage Completion (Funnel)</h3>
            <p className="chart-subtitle">Progress metrics of audio processing through transcription, summarizing, and final minutes drafting</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={charts.pipeline_funnel} layout="vertical">
                  <XAxis type="number" stroke="#9ca3af" tickLine={false} />
                  <YAxis dataKey="stage" type="category" stroke="#9ca3af" tickLine={false} width={130} />
                  <Tooltip content={<CustomTooltip />} cursor={false} />
                  <Bar dataKey="count" name="Jobs Completed" fill="#a78bfa" radius={[0, 4, 4, 0]} barSize={25} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Meeting Speaker Distribution</h3>
            <p className="chart-subtitle">Proportion of unique speaker counts detected in uploaded audio records</p>
            <div className="chart-wrapper pie-wrapper">
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={charts.speaker_breakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {charts.speaker_breakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#a78bfa', '#f59e0b', '#3b82f6', '#10b981'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass span-3">
            <h3>Daily Meetings Audio Input</h3>
            <p className="chart-subtitle">Total audio records uploaded and processed over the last 15 days</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={charts.daily_meeting_trend}>
                  <defs>
                    <linearGradient id="colorMom" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#a78bfa" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#9ca3af" tickLine={false} />
                  <YAxis stroke="#9ca3af" tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="count" name="Meetings Processed" stroke="#a78bfa" strokeWidth={2} fillOpacity={1} fill="url(#colorMom)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (toolKey === "overall") {
    return (
      <div className="insights-container">
        <div className="metrics-grid">
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Registered Users</span>
              <Users className="icon text-primary" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.total_users}</span>
              <span className="subtext">Total platform accounts</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Active (7d)</span>
              <Users className="icon text-emerald" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.active_7d_users}</span>
              <span className="subtext">Logged in within last 7 days</span>
            </div>
          </div>
          <div className="metric-card glass">
            <div className="card-header">
              <span className="card-title">Dormant Users</span>
              <Users className="icon text-orange" size={20} />
            </div>
            <div className="card-body">
              <span className="value">{metrics.dormant_users}</span>
              <span className="subtext">Inactive for more than 7 days</span>
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card glass span-2">
            <h3>Leaderboard: Power Users</h3>
            <p className="chart-subtitle">Most active profiles ranked by login activity count</p>
            <div className="table-wrapper">
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>User</th>
                    <th>Visits</th>
                  </tr>
                </thead>
                <tbody>
                  {charts.power_users.map((user, idx) => (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td>{user.username}</td>
                      <td><strong>{user.visits}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Tool Category Usage</h3>
            <p className="chart-subtitle">Total documents uploaded grouped by tool modules</p>
            <div className="chart-wrapper pie-wrapper">
              <ResponsiveContainer width="100%" height={230}>
                <PieChart>
                  <Pie
                    data={charts.category_usage}
                    cx="50%"
                    cy="50%"
                    innerRadius={0}
                    outerRadius={75}
                    paddingAngle={0}
                    dataKey="value"
                  >
                    {charts.category_usage.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#8b5cf6', '#3b82f6', '#10b981', '#ec4899', '#f59e0b', '#ef4444'][index % 6]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass span-2">
            <h3>Platform Tool Health Leaderboard</h3>
            <p className="chart-subtitle">Leaderboard of active tools ranked by computed Health Score (0-100)</p>
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={charts.health_leaderboard} layout="vertical">
                  <XAxis type="number" domain={[0, 100]} stroke="#9ca3af" tickLine={false} />
                  <YAxis dataKey="tool" type="category" stroke="#9ca3af" tickLine={false} width={130} />
                  <Tooltip cursor={false} />
                  <Bar dataKey="score" name="Health Score" fill="#10b981" radius={[0, 4, 4, 0]} barSize={20}>
                    {charts.health_leaderboard.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.score > 85 ? '#10b981' : entry.score > 75 ? '#3b82f6' : '#ec4899'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Speed vs. Satisfaction</h3>
            <p className="chart-subtitle">Cross-tool comparison of average latency vs customer approval rate</p>
            <div className="table-wrapper">
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th>Feature Tool</th>
                    <th>Avg Speed</th>
                    <th>Thumbs Up</th>
                  </tr>
                </thead>
                <tbody>
                  {charts.satisfaction_speed.map((row, idx) => (
                    <tr key={idx}>
                      <td>{row.tool}</td>
                      <td><strong>{row.latency}s</strong></td>
                      <td>
                        <span style={{ 
                          color: row.satisfaction > 75 ? '#10b981' : row.satisfaction > 70 ? '#3b82f6' : '#ec4899',
                          fontWeight: 'bold' 
                        }}>
                          {row.satisfaction}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <div className="loading-text">Select a tool to show graphs</div>;
}
