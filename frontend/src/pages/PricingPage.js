import { motion } from 'framer-motion';
import { Check, ArrowRight, Star, Zap } from 'lucide-react';
import { pricingPlans } from '../data/mockData';

export default function PricingPage() {
  const handlePlanSelect = (planName) => {
    if (planName === 'Enterprise') {
      alert('Contact sales form would open here. This is a prototype.');
    } else {
      alert(`${planName} plan selected. Payment flow would start here. This is a prototype.`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300" data-testid="pricing-page">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 dark:bg-primary/20 border border-primary/20 mb-6">
            <Zap size={14} className="text-primary" />
            <span className="text-xs font-semibold text-primary tracking-wide uppercase">Simple Pricing</span>
          </div>
          <h1 className="font-heading text-4xl md:text-6xl font-bold text-slate-900 dark:text-white tracking-tight" data-testid="pricing-title">
            Choose your plan
          </h1>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
            Start free, scale as you grow. Every plan includes core compliance scanning.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {pricingPlans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.12 }}
              data-testid={`pricing-card-${plan.name.toLowerCase()}`}
              className={`relative rounded-2xl border p-8 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                plan.highlighted
                  ? 'border-primary bg-white dark:bg-slate-900 shadow-lg shadow-primary/10 scale-[1.02]'
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900'
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-primary text-white text-xs font-bold rounded-full shadow-lg shadow-primary/25">
                    <Star size={12} fill="currentColor" />
                    {plan.badge}
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="font-heading text-xl font-bold text-slate-900 dark:text-white">{plan.name}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{plan.description}</p>
              </div>

              <div className="mb-8">
                <span className="font-heading text-5xl font-extrabold text-slate-900 dark:text-white">{plan.price}</span>
                <span className="text-sm text-slate-500 dark:text-slate-400 ml-1">{plan.period}</span>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map(feature => (
                  <li key={feature} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Check size={12} className="text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <span className="text-sm text-slate-600 dark:text-slate-400">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                data-testid={`pricing-cta-${plan.name.toLowerCase()}`}
                onClick={() => handlePlanSelect(plan.name)}
                className={`w-full py-3 rounded-lg font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 ${
                  plan.highlighted
                    ? 'bg-primary text-white hover:bg-primary-hover shadow-lg shadow-primary/25 hover:shadow-primary/40 active:scale-[0.97]'
                    : 'border-2 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-primary hover:text-primary dark:hover:border-primary dark:hover:text-primary'
                }`}
              >
                {plan.cta}
                <ArrowRight size={16} />
              </button>
            </motion.div>
          ))}
        </div>

        {/* FAQ / Note */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-16 text-center"
        >
          <p className="text-sm text-slate-500 dark:text-slate-500">
            All plans include 14-day free trial. No credit card required to start.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
