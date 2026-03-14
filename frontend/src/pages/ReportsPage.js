import { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, FileWarning, Search, ChevronDown, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { reportsData } from '../data/mockData';

const statusStyles = {
  Completed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  'In Progress': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
};

export default function ReportsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [exportingId, setExportingId] = useState(null);

  const filtered = reportsData.filter(r =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.jurisdictions.some(j => j.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleExport = (id) => {
    setExportingId(id);
    setTimeout(() => setExportingId(null), 1500);
  };

  const handleGenerateWhitepaper = () => {
    alert('Security Whitepaper generation started. This is a prototype action.');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300" data-testid="reports-page">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="font-heading text-3xl font-bold text-slate-900 dark:text-white" data-testid="reports-title">Reports</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{reportsData.length} compliance reports generated</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              data-testid="generate-whitepaper-btn"
              onClick={handleGenerateWhitepaper}
              className="inline-flex items-center gap-2 px-4 py-2.5 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-medium text-sm rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <FileWarning size={16} />
              Generate Security Whitepaper
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              data-testid="reports-search"
              type="text"
              placeholder="Search reports..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-colors placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Reports Table */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-white dark:bg-slate-900"
        >
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="reports-table">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/50 text-left">
                  <th className="px-5 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Report</th>
                  <th className="px-5 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Date</th>
                  <th className="px-5 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Jurisdictions</th>
                  <th className="px-5 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Findings</th>
                  <th className="px-5 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Status</th>
                  <th className="px-5 py-3.5 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filtered.map((report) => (
                  <tr
                    key={report.id}
                    data-testid={`report-row-${report.id}`}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 dark:bg-primary/20 flex items-center justify-center flex-shrink-0">
                          <FileText size={14} className="text-primary" />
                        </div>
                        <span className="text-sm font-medium text-slate-900 dark:text-white">{report.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-500 dark:text-slate-400">{report.date}</td>
                    <td className="px-5 py-4">
                      <div className="flex flex-wrap gap-1.5">
                        {report.jurisdictions.map(j => (
                          <span key={j} className="px-2 py-0.5 text-[10px] font-semibold rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {j}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2 text-xs">
                        {report.findingsSummary.critical > 0 && (
                          <span className="flex items-center gap-0.5 text-red-500">
                            <AlertCircle size={10} />
                            {report.findingsSummary.critical}
                          </span>
                        )}
                        {report.findingsSummary.high > 0 && (
                          <span className="flex items-center gap-0.5 text-orange-500">
                            <AlertTriangle size={10} />
                            {report.findingsSummary.high}
                          </span>
                        )}
                        {report.findingsSummary.medium > 0 && (
                          <span className="flex items-center gap-0.5 text-amber-500">
                            <AlertTriangle size={10} />
                            {report.findingsSummary.medium}
                          </span>
                        )}
                        {report.findingsSummary.low > 0 && (
                          <span className="flex items-center gap-0.5 text-blue-500">
                            <Info size={10} />
                            {report.findingsSummary.low}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${statusStyles[report.status]}`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <button
                        data-testid={`export-pdf-btn-${report.id}`}
                        onClick={() => handleExport(report.id)}
                        disabled={exportingId === report.id}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
                      >
                        <Download size={12} />
                        {exportingId === report.id ? 'Exporting...' : 'Export PDF'}
                      </button>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-5 py-12 text-center text-slate-500">
                      No reports found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
