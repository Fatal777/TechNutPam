import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Download, ToggleRight, Code, ArrowRight, Terminal, Check } from 'lucide-react';

const fadeUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: 'easeOut' },
};

const stagger = {
  animate: { transition: { staggerChildren: 0.12 } },
};

const steps = [
  { icon: Download, title: 'Install MCP', desc: 'One command to add compliance scanning to your IDE' },
  { icon: ToggleRight, title: 'Toggle Jurisdictions', desc: 'Enable GDPR, HIPAA, SOC2, DPDP or any combo' },
  { icon: Code, title: 'Code Compliantly', desc: 'Get real-time fixes as you write code' },
];

const features = [
  'Real-time compliance scanning',
  'Auto-fix suggestions with code diffs',
  'Multi-jurisdiction support',
  'Dependency vulnerability checks',
  'PDF report generation',
  'CI/CD pipeline integration',
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-emerald-500/5 dark:from-primary/10 dark:to-emerald-500/10" />
        <div className="relative max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 md:pt-24 md:pb-32">
          <motion.div
            variants={stagger}
            initial="initial"
            animate="animate"
            className="grid grid-cols-1 md:grid-cols-12 gap-12 items-center"
          >
            <div className="md:col-span-7 space-y-8">
              <motion.div variants={fadeUp} className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-100 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800">
                <Shield size={14} className="text-emerald-600 dark:text-emerald-400" />
                <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 tracking-wide uppercase">AI-Powered Compliance</span>
              </motion.div>

              <motion.h1
                variants={fadeUp}
                data-testid="hero-title"
                className="font-heading text-5xl md:text-7xl font-extrabold text-slate-900 dark:text-white leading-[1.05] tracking-tight"
              >
                Your Legal<br />
                Department<br />
                <span className="text-primary">in a Box</span>
              </motion.h1>

              <motion.p
                variants={fadeUp}
                data-testid="hero-subtitle"
                className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-lg leading-relaxed"
              >
                AI compliance agent that lives in your IDE. Scan, detect, and fix regulatory violations before they ship.
              </motion.p>

              <motion.div variants={fadeUp} className="flex flex-wrap gap-4">
                <Link
                  to="/dashboard"
                  data-testid="cta-get-started"
                  className="inline-flex items-center gap-2 px-7 py-3.5 bg-primary text-white font-semibold rounded-lg shadow-lg shadow-primary/25 hover:bg-primary-hover hover:shadow-primary/40 transition-all duration-200 active:scale-[0.97]"
                >
                  Get Started Free
                  <ArrowRight size={18} />
                </Link>
                <Link
                  to="/pricing"
                  data-testid="cta-view-pricing"
                  className="inline-flex items-center gap-2 px-7 py-3.5 border-2 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-lg hover:border-primary hover:text-primary dark:hover:border-primary dark:hover:text-primary transition-all duration-200"
                >
                  View Pricing
                </Link>
              </motion.div>
            </div>

            <motion.div variants={fadeUp} className="md:col-span-5">
              <div className="relative">
                <div className="absolute -inset-4 bg-gradient-to-br from-primary/20 to-emerald-500/20 rounded-2xl blur-2xl opacity-50" />
                <div className="relative bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-2xl">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-amber-500" />
                    <div className="w-3 h-3 rounded-full bg-emerald-500" />
                    <span className="ml-3 text-xs text-slate-500 font-code">terminal</span>
                  </div>
                  <div className="space-y-3 font-code text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-emerald-400">$</span>
                      <span className="text-slate-300">claude mcp add compliance-shield</span>
                    </div>
                    <div className="text-slate-500">Installing ComplianceShield MCP...</div>
                    <div className="flex items-center gap-2 text-emerald-400">
                      <Check size={14} />
                      <span>MCP server connected</span>
                    </div>
                    <div className="flex items-center gap-2 text-emerald-400">
                      <Check size={14} />
                      <span>GDPR rules loaded (847 rules)</span>
                    </div>
                    <div className="flex items-center gap-2 text-emerald-400">
                      <Check size={14} />
                      <span>Ready to scan</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section data-testid="how-it-works-section" className="py-20 md:py-32 bg-white dark:bg-slate-900/50">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-heading text-4xl md:text-5xl font-bold text-slate-900 dark:text-white tracking-tight">
              How it works
            </h2>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">Three steps to compliant code</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {steps.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                data-testid={`step-card-${i + 1}`}
                className="relative text-center group"
              >
                {i < 2 && (
                  <div className="hidden md:block absolute top-10 left-[60%] w-[80%] border-t-2 border-dashed border-slate-300 dark:border-slate-700" />
                )}
                <div className="relative z-10 w-20 h-20 mx-auto mb-6 rounded-2xl bg-primary/10 dark:bg-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                  <step.icon size={32} className="text-primary" />
                </div>
                <h3 className="font-heading text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  {step.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                  {step.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Setup Command */}
      <section data-testid="setup-section" className="py-20 md:py-28">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="space-y-6"
            >
              <h2 className="font-heading text-4xl md:text-5xl font-bold text-slate-900 dark:text-white tracking-tight">
                One-line setup
              </h2>
              <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed">
                Start scanning your codebase for compliance issues in seconds. No complex configuration needed.
              </p>
              <div className="space-y-3">
                {features.slice(0, 4).map(f => (
                  <div key={f} className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center flex-shrink-0">
                      <Check size={12} className="text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <span className="text-slate-700 dark:text-slate-300 text-sm">{f}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
                <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800">
                  <Terminal size={14} className="text-slate-500" />
                  <span className="text-xs text-slate-500 font-code">Setup Command</span>
                </div>
                <div className="p-6">
                  <code className="font-code text-sm md:text-base text-emerald-400 break-all leading-relaxed">
                    claude mcp add compliance-shield --transport sse https://complianceshield.dev/mcp
                  </code>
                </div>
              </div>
              <p className="mt-4 text-sm text-slate-500 dark:text-slate-500 text-center">
                Works with Claude, Cursor, VS Code, and any MCP-compatible client
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 md:py-28 bg-white dark:bg-slate-900/50">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-heading text-4xl md:text-5xl font-bold text-slate-900 dark:text-white tracking-tight">
              Everything you need
            </h2>
          </motion.div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {features.map((f, i) => (
              <motion.div
                key={f}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 dark:bg-primary/20 flex items-center justify-center mb-4">
                  <Check size={18} className="text-primary" />
                </div>
                <p className="font-medium text-slate-900 dark:text-white">{f}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 md:py-28">
        <div className="max-w-3xl mx-auto text-center px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="space-y-8"
          >
            <h2 className="font-heading text-4xl md:text-5xl font-bold text-slate-900 dark:text-white tracking-tight">
              Ship compliant code today
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-400">
              Join thousands of developers who trust ComplianceShield to keep their code regulation-ready.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link
                to="/dashboard"
                data-testid="cta-bottom-get-started"
                className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-white font-semibold rounded-lg shadow-lg shadow-primary/25 hover:bg-primary-hover hover:shadow-primary/40 transition-all duration-200 active:scale-[0.97]"
              >
                Get Started Free
                <ArrowRight size={18} />
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center gap-2 px-8 py-4 border-2 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-lg hover:border-primary hover:text-primary transition-all duration-200"
              >
                View Pricing
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
