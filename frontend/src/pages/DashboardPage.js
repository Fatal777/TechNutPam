import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, AlertTriangle, AlertCircle, Info, Shield, Package, ChevronRight, Newspaper, Globe, ExternalLink } from 'lucide-react';
import { scanResults, dependencyResults, complianceNews, flaggedWebsites } from '../data/mockData';

const severityConfig = {
  Critical: { color: 'bg-red-500', text: 'text-red-500', badge: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800', icon: AlertCircle },
  High: { color: 'bg-orange-500', text: 'text-orange-500', badge: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800', icon: AlertTriangle },
  Medium: { color: 'bg-amber-500', text: 'text-amber-500', badge: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800', icon: AlertTriangle },
  Low: { color: 'bg-blue-500', text: 'text-blue-500', badge: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800', icon: Info },
};

const jurisdictionColors = {
  GDPR: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  'DPDP India': 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
  HIPAA: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
  SOC2: 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400',
};

function SeverityBars({ severity }) {
  const bars = [
    { key: 'critical', color: 'bg-red-500', count: severity.critical },
    { key: 'high', color: 'bg-orange-500', count: severity.high },
    { key: 'medium', color: 'bg-amber-500', count: severity.medium },
    { key: 'low', color: 'bg-blue-500', count: severity.low },
  ];
  return (
    <div className="flex items-end gap-0.5 h-5">
      {bars.map(b => (
        <div
          key={b.key}
          className={`w-1.5 rounded-t-sm ${b.count > 0 ? b.color : 'bg-slate-700/30'}`}
          style={{ height: b.count > 0 ? `${Math.min(20, 6 + b.count * 5)}px` : '4px' }}
          title={`${b.key}: ${b.count}`}
        />
      ))}
    </div>
  );
}

function DetailPanel({ scan, onClose }) {
  const [acceptedFixes, setAcceptedFixes] = useState({});

  if (!scan) return null;

  const handleAcceptFix = (idx) => {
    setAcceptedFixes(prev => ({ ...prev, [idx]: true }));
  };

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed inset-y-0 right-0 w-full max-w-xl bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl z-50 overflow-y-auto"
    >
      <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border-b border-slate-200 dark:border-slate-800">
        <h3 className="font-heading font-bold text-lg text-slate-900 dark:text-white" data-testid="detail-panel-title">{scan.file}</h3>
        <button
          onClick={onClose}
          data-testid="detail-panel-close"
          className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <X size={18} className="text-slate-500" />
        </button>
      </div>

      <div className="p-6 space-y-6">
        {scan.details.map((finding, idx) => {
          const sev = severityConfig[finding.severity];
          return (
            <div
              key={idx}
              data-testid={`finding-card-${idx}`}
              className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden"
            >
              <div className="p-5 space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full border ${sev.badge}`}>
                    <sev.icon size={12} />
                    {finding.severity}
                  </span>
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${jurisdictionColors[finding.jurisdiction]}`}>
                    {finding.jurisdiction}
                  </span>
                </div>

                <div>
                  <h4 className="font-heading font-semibold text-slate-900 dark:text-white text-sm">Rule Violated</h4>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{finding.rule}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">{finding.description}</p>
                </div>

                <div>
                  <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Violation</p>
                  <div className="rounded-lg bg-slate-950 border border-red-500/20 p-4 overflow-x-auto">
                    <pre className="font-code text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                      {finding.violationCode.split('\n').map((line, i) => (
                        <div
                          key={i}
                          className={finding.violationLines?.includes(i + 1) ? 'bg-red-500/15 -mx-4 px-4 border-l-2 border-red-500' : ''}
                        >
                          {line}
                        </div>
                      ))}
                    </pre>
                  </div>
                </div>

                <div>
                  <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Fixed Code</p>
                  <div className="rounded-lg bg-slate-950 border border-emerald-500/20 p-4 overflow-x-auto">
                    <pre className="font-code text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
                      {finding.fixedCode.split('\n').map((line, i) => (
                        <div key={i} className="bg-emerald-500/10 -mx-4 px-4 border-l-2 border-emerald-500">
                          {line}
                        </div>
                      ))}
                    </pre>
                  </div>
                </div>

                <button
                  data-testid={`accept-fix-btn-${idx}`}
                  onClick={() => handleAcceptFix(idx)}
                  disabled={acceptedFixes[idx]}
                  className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 ${
                    acceptedFixes[idx]
                      ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 cursor-default'
                      : 'bg-primary text-white hover:bg-primary-hover shadow-md hover:shadow-lg active:scale-[0.98]'
                  }`}
                >
                  {acceptedFixes[idx] ? (
                    <span className="flex items-center justify-center gap-2"><Check size={16} /> Fix Accepted</span>
                  ) : (
                    'Accept Fix'
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}

const newsSeverityStyle = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

const newsJurisdictionStyle = {
  GDPR: 'bg-purple-500/20 text-purple-400',
  DPDP: 'bg-teal-500/20 text-teal-400',
  HIPAA: 'bg-rose-500/20 text-rose-400',
  SOC2: 'bg-sky-500/20 text-sky-400',
};

export default function DashboardPage() {
  const [jurisdictions, setJurisdictions] = useState({
    GDPR: true,
    'DPDP India': true,
    HIPAA: true,
    SOC2: true,
  });
  const [selectedScan, setSelectedScan] = useState(null);
  const [activeTab, setActiveTab] = useState('scans');

  const toggleJurisdiction = (key) => {
    setJurisdictions(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const activeJurisdictions = Object.entries(jurisdictions).filter(([, v]) => v).map(([k]) => k);
  const filteredScans = scanResults.filter(s =>
    s.jurisdictions.some(j => activeJurisdictions.includes(j))
  );

  const jurisdictionMap = { 'DPDP India': 'DPDP' };
  const normalizedActive = activeJurisdictions.map(j => jurisdictionMap[j] || j);

  const filteredNews = complianceNews.filter(n =>
    normalizedActive.includes(n.jurisdiction)
  );
  const filteredFlagged = flaggedWebsites.filter(w =>
    w.jurisdictions.some(j => normalizedActive.includes(j))
  );

  return (
    <div className="flex h-[calc(100vh-64px)] bg-slate-950 text-white" data-testid="dashboard-page">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 border-r border-slate-800 bg-slate-900/80 p-5" data-testid="jurisdiction-sidebar">
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Active</h3>
        <div className="space-y-3">
          {Object.entries(jurisdictions).map(([key, enabled]) => (
            <div key={key} className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">{key}</span>
              <button
                data-testid={`jurisdiction-toggle-${key.replace(/\s/g, '-').toLowerCase()}`}
                onClick={() => toggleJurisdiction(key)}
                className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${
                  enabled ? 'bg-emerald-500' : 'bg-slate-700'
                }`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                    enabled ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>

        {/* CrustData powered badge */}
        <div className="mt-8 pt-5 border-t border-slate-800">
          <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-wider mb-3">Intelligence</p>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>CrustData Live Feed</span>
          </div>
          <p className="text-[10px] text-slate-600 mt-1 pl-3.5">Updated 2 min ago</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Tab Bar */}
        <div className="flex items-center gap-1 px-6 pt-5 pb-0">
          {[
            { key: 'scans', label: 'Scan Results', icon: Shield },
            { key: 'news', label: 'Compliance News', icon: Newspaper },
            { key: 'flagged', label: 'Flagged Websites', icon: Globe },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-sm font-semibold transition-colors ${
                activeTab === tab.key
                  ? 'bg-slate-800/80 text-white border border-slate-700 border-b-slate-800/80'
                  : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/30'
              }`}
            >
              <tab.icon size={14} />
              {tab.label}
              {tab.key === 'news' && filteredNews.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-400">
                  {filteredNews.length}
                </span>
              )}
              {tab.key === 'flagged' && filteredFlagged.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-red-500/20 text-red-400">
                  {filteredFlagged.length}
                </span>
              )}
            </button>
          ))}
        </div>

        <div className="flex-1 flex overflow-hidden">
          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto p-6 pt-4">
            {/* Scan Results Tab */}
            {activeTab === 'scans' && (
              <>
                <h2 className="font-heading text-xl font-bold mb-5" data-testid="scan-results-title">Recent Scan Results</h2>
                <div className="rounded-xl border border-slate-800 overflow-hidden">
                  <table className="w-full" data-testid="scan-results-table">
                    <thead>
                      <tr className="bg-slate-800/50 text-left">
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Timestamp</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">File</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider text-center">Findings</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Severity</th>
                        <th className="px-4 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {filteredScans.map(scan => (
                        <tr
                          key={scan.id}
                          data-testid={`scan-row-${scan.id}`}
                          onClick={() => setSelectedScan(scan)}
                          className={`cursor-pointer transition-colors hover:bg-slate-800/40 ${
                            selectedScan?.id === scan.id ? 'bg-slate-800/60' : ''
                          }`}
                        >
                          <td className="px-4 py-3.5 text-sm text-slate-400 font-code">{scan.timestamp}</td>
                          <td className="px-4 py-3.5 text-sm text-slate-200 font-medium">{scan.file}</td>
                          <td className="px-4 py-3.5 text-sm text-center text-slate-200 font-semibold">{scan.findings}</td>
                          <td className="px-4 py-3.5"><SeverityBars severity={scan.severity} /></td>
                          <td className="px-4 py-3.5">
                            <ChevronRight size={16} className="text-slate-600" />
                          </td>
                        </tr>
                      ))}
                      {filteredScans.length === 0 && (
                        <tr>
                          <td colSpan={5} className="px-4 py-12 text-center text-slate-500">
                            No scan results for selected jurisdictions
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}

            {/* Compliance News Tab */}
            {activeTab === 'news' && (
              <>
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-heading text-xl font-bold">Live Compliance News</h2>
                  <span className="flex items-center gap-1.5 text-xs text-emerald-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Powered by CrustData
                  </span>
                </div>
                <div className="space-y-3">
                  {filteredNews.map(item => (
                    <motion.div
                      key={item.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${newsSeverityStyle[item.severity]}`}>
                              {item.severity.toUpperCase()}
                            </span>
                            <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${newsJurisdictionStyle[item.jurisdiction]}`}>
                              {item.jurisdiction}
                            </span>
                            <span className="text-[10px] text-slate-600">{item.date}</span>
                          </div>
                          <h3 className="font-heading font-semibold text-sm text-slate-200 mb-1.5">{item.title}</h3>
                          <p className="text-xs text-slate-400 leading-relaxed">{item.snippet}</p>
                          <p className="text-[10px] text-slate-600 mt-2">Source: {item.source}</p>
                        </div>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center hover:bg-slate-800 transition-colors"
                        >
                          <ExternalLink size={14} className="text-slate-500" />
                        </a>
                      </div>
                    </motion.div>
                  ))}
                  {filteredNews.length === 0 && (
                    <div className="py-12 text-center text-slate-500">
                      No compliance news for selected jurisdictions
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Flagged Websites Tab */}
            {activeTab === 'flagged' && (
              <>
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-heading text-xl font-bold">Flagged Websites</h2>
                  <span className="flex items-center gap-1.5 text-xs text-emerald-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    CrustData Web Search
                  </span>
                </div>
                <div className="rounded-xl border border-slate-800 overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-slate-800/50 text-left">
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Website</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Compliance Issues</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Frameworks</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Severity</th>
                        <th className="px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Scanned</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {filteredFlagged.map(site => (
                        <tr key={site.id} className="hover:bg-slate-800/30 transition-colors">
                          <td className="px-4 py-3.5">
                            <div className="flex items-center gap-2">
                              <Globe size={14} className="text-slate-500 flex-shrink-0" />
                              <span className="text-sm text-slate-200 font-medium font-code">{site.url}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3.5">
                            <div className="space-y-1">
                              {site.issues.map((issue, i) => (
                                <div key={i} className="flex items-center gap-1.5 text-xs text-slate-400">
                                  <AlertCircle size={10} className="text-red-400 flex-shrink-0" />
                                  {issue}
                                </div>
                              ))}
                            </div>
                          </td>
                          <td className="px-4 py-3.5">
                            <div className="flex flex-wrap gap-1">
                              {site.jurisdictions.map(j => (
                                <span key={j} className={`px-2 py-0.5 text-[10px] font-bold rounded ${newsJurisdictionStyle[j]}`}>
                                  {j}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-4 py-3.5">
                            <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${newsSeverityStyle[site.severity]}`}>
                              {site.severity.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-4 py-3.5 text-xs text-slate-500">{site.scanDate}</td>
                        </tr>
                      ))}
                      {filteredFlagged.length === 0 && (
                        <tr>
                          <td colSpan={5} className="px-4 py-12 text-center text-slate-500">
                            No flagged websites for selected jurisdictions
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>

          {/* Dependency Scan Panel */}
          <aside className="w-64 flex-shrink-0 border-l border-slate-800 bg-slate-900/50 p-5 overflow-y-auto" data-testid="dependency-panel">
            <div className="flex items-center gap-2 mb-5">
              <Package size={16} className="text-slate-400" />
              <h3 className="font-heading text-sm font-bold text-slate-300">Dependency Scan</h3>
            </div>
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-3">SafeDep Results</p>
            <div className="space-y-3">
              {dependencyResults.map((dep, i) => (
                <div key={i} data-testid={`dep-item-${dep.name}`} className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        dep.status === 'Safe'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}
                    >
                      {dep.status}
                    </span>
                    <span className="text-sm text-slate-300 font-medium truncate">{dep.name}</span>
                  </div>
                  <p className="text-[10px] text-slate-600 pl-1">{dep.lastChecked}</p>
                </div>
              ))}
            </div>
          </aside>
        </div>
      </main>

      {/* Detail Panel Overlay */}
      <AnimatePresence>
        {selectedScan && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/40 z-40"
              onClick={() => setSelectedScan(null)}
            />
            <DetailPanel scan={selectedScan} onClose={() => setSelectedScan(null)} />
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
