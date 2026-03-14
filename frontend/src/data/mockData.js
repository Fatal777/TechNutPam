export const scanResults = [
  {
    id: 1,
    timestamp: "2024-01-15 14:32:00",
    file: "src/api.js",
    findings: 3,
    severity: { critical: 1, high: 1, medium: 1, low: 0 },
    jurisdictions: ["GDPR"],
    details: [
      {
        severity: "Critical",
        jurisdiction: "GDPR",
        rule: "Right to Erasure Implementation Error",
        description: "User data deletion endpoint does not remove all associated records from secondary storage.",
        violationCode: `export default = divalnx() {
  const count = {1};

  const acceptcs(() => {
    system.out.ernslinert("Tre...");
  });
};`,
        fixedCode: `export default = Scans (
  const acceptsr(() => {
    system.out.acgslinert("Tre..."),
  );
};`,
        violationLines: [4, 5],
      },
      {
        severity: "High",
        jurisdiction: "GDPR",
        rule: "Data Processing Agreement Missing",
        description: "Third-party API call lacks data processing agreement validation before transmitting PII.",
        violationCode: `const sendToAnalytics = (userData) => {
  // No DPA check before sending data
  fetch('/api/analytics', {
    body: JSON.stringify(userData)
  });
};`,
        fixedCode: `const sendToAnalytics = async (userData) => {
  const dpaValid = await checkDPA('analytics');
  if (!dpaValid) throw new Error('DPA required');
  fetch('/api/analytics', {
    body: JSON.stringify(userData)
  });
};`,
        violationLines: [2, 3],
      },
      {
        severity: "Medium",
        jurisdiction: "GDPR",
        rule: "Consent Collection Incomplete",
        description: "Form collects email without explicit opt-in consent checkbox.",
        violationCode: `<form onSubmit={handleSubmit}>
  <input type="email" name="email" />
  <button type="submit">Subscribe</button>
</form>`,
        fixedCode: `<form onSubmit={handleSubmit}>
  <input type="email" name="email" />
  <label>
    <input type="checkbox" required name="consent" />
    I agree to the privacy policy
  </label>
  <button type="submit">Subscribe</button>
</form>`,
        violationLines: [2],
      },
    ],
  },
  {
    id: 2,
    timestamp: "2024-01-15 14:28:00",
    file: "src/auth.js",
    findings: 1,
    severity: { critical: 0, high: 0, medium: 1, low: 0 },
    jurisdictions: ["HIPAA"],
    details: [
      {
        severity: "Medium",
        jurisdiction: "HIPAA",
        rule: "PHI Access Logging Absent",
        description: "Protected Health Information access is not being logged for audit trail.",
        violationCode: `const getPatientData = (id) => {
  return db.patients.findOne({ id });
};`,
        fixedCode: `const getPatientData = (id) => {
  auditLog.record('PHI_ACCESS', { patientId: id });
  return db.patients.findOne({ id });
};`,
        violationLines: [1, 2],
      },
    ],
  },
  {
    id: 3,
    timestamp: "2024-01-15 14:15:00",
    file: "src/storage.js",
    findings: 2,
    severity: { critical: 0, high: 1, medium: 0, low: 1 },
    jurisdictions: ["DPDP India"],
    details: [
      {
        severity: "High",
        jurisdiction: "DPDP India",
        rule: "Data Localization Violation",
        description: "User data stored on servers outside India without data principal consent.",
        violationCode: `const uploadFile = (data) => {
  s3.upload({ Bucket: 'us-east-1-store', Body: data });
};`,
        fixedCode: `const uploadFile = (data, region) => {
  const bucket = region === 'IN' ? 'ap-south-1-store' : 'us-east-1-store';
  if (region === 'IN') validateLocalStorage(data);
  s3.upload({ Bucket: bucket, Body: data });
};`,
        violationLines: [2],
      },
      {
        severity: "Low",
        jurisdiction: "DPDP India",
        rule: "Privacy Notice Language",
        description: "Privacy notice not available in local language as required.",
        violationCode: `const privacyNotice = {
  lang: 'en',
  content: 'Your data will be processed...'
};`,
        fixedCode: `const privacyNotice = {
  lang: ['en', 'hi'],
  content: {
    en: 'Your data will be processed...',
    hi: 'Aapka data process kiya jaayega...'
  }
};`,
        violationLines: [2],
      },
    ],
  },
  {
    id: 4,
    timestamp: "2024-01-15 13:55:00",
    file: "src/logging.js",
    findings: 4,
    severity: { critical: 1, high: 1, medium: 1, low: 1 },
    jurisdictions: ["SOC2"],
    details: [
      {
        severity: "Critical",
        jurisdiction: "SOC2",
        rule: "Encryption at Rest Missing",
        description: "Sensitive log data stored without encryption.",
        violationCode: `fs.writeFileSync('/var/logs/app.log', sensitiveData);`,
        fixedCode: `const encrypted = encrypt(sensitiveData, process.env.LOG_KEY);
fs.writeFileSync('/var/logs/app.log.enc', encrypted);`,
        violationLines: [1],
      },
      {
        severity: "High",
        jurisdiction: "SOC2",
        rule: "Access Control Inadequate",
        description: "Log files accessible without proper role-based access control.",
        violationCode: `app.get('/logs', (req, res) => {
  res.sendFile('/var/logs/app.log');
});`,
        fixedCode: `app.get('/logs', rbac('admin'), (req, res) => {
  res.sendFile('/var/logs/app.log');
});`,
        violationLines: [1],
      },
      {
        severity: "Medium",
        jurisdiction: "SOC2",
        rule: "Audit Trail Incomplete",
        description: "User actions not fully tracked in audit log.",
        violationCode: `const updateUser = (id, data) => {
  db.users.update({ id }, data);
};`,
        fixedCode: `const updateUser = (id, data) => {
  auditTrail.log({ action: 'UPDATE_USER', userId: id, changes: data });
  db.users.update({ id }, data);
};`,
        violationLines: [2],
      },
      {
        severity: "Low",
        jurisdiction: "SOC2",
        rule: "Log Rotation Policy",
        description: "No automatic log rotation configured.",
        violationCode: `// No log rotation configured
const logger = new Logger({ file: '/var/logs/app.log' });`,
        fixedCode: `const logger = new Logger({
  file: '/var/logs/app.log',
  maxSize: '10m',
  maxFiles: '14d',
  compress: true
});`,
        violationLines: [1],
      },
    ],
  },
  {
    id: 5,
    timestamp: "2024-01-15 13:40:00",
    file: "src/payments.js",
    findings: 2,
    severity: { critical: 0, high: 1, medium: 1, low: 0 },
    jurisdictions: ["GDPR", "DPDP India"],
    details: [
      {
        severity: "High",
        jurisdiction: "GDPR",
        rule: "Payment Data Retention",
        description: "Credit card data retained beyond transaction completion.",
        violationCode: `const processPayment = (card) => {
  db.payments.insert({ cardNumber: card.number, cvv: card.cvv });
  chargeCard(card);
};`,
        fixedCode: `const processPayment = (card) => {
  const token = tokenize(card);
  db.payments.insert({ token, last4: card.number.slice(-4) });
  chargeCard(token);
};`,
        violationLines: [2],
      },
      {
        severity: "Medium",
        jurisdiction: "DPDP India",
        rule: "Cross-border Transfer Notice",
        description: "Payment processor transfers data internationally without notice.",
        violationCode: `const gateway = new PaymentGateway({ region: 'US' });`,
        fixedCode: `const gateway = new PaymentGateway({
  region: 'IN',
  crossBorderNotice: true,
  consentRequired: true
});`,
        violationLines: [1],
      },
    ],
  },
  {
    id: 6,
    timestamp: "2024-01-15 13:25:00",
    file: "src/cache.js",
    findings: 2,
    severity: { critical: 0, high: 0, medium: 1, low: 1 },
    jurisdictions: ["HIPAA"],
    details: [
      {
        severity: "Medium",
        jurisdiction: "HIPAA",
        rule: "Cache Expiration for PHI",
        description: "Cached PHI data does not have proper TTL settings.",
        violationCode: `redis.set('patient_' + id, JSON.stringify(phiData));`,
        fixedCode: `redis.set('patient_' + id, encrypt(JSON.stringify(phiData)), 'EX', 3600);`,
        violationLines: [1],
      },
      {
        severity: "Low",
        jurisdiction: "HIPAA",
        rule: "Cache Key Naming",
        description: "Cache keys contain identifiable patient information.",
        violationCode: `const key = 'patient_john_doe_12345';`,
        fixedCode: `const key = 'patient_' + hash('john_doe_12345');`,
        violationLines: [1],
      },
    ],
  },
  {
    id: 7,
    timestamp: "2024-01-15 13:10:00",
    file: "src/email.js",
    findings: 3,
    severity: { critical: 0, high: 1, medium: 1, low: 1 },
    jurisdictions: ["GDPR"],
    details: [
      {
        severity: "High",
        jurisdiction: "GDPR",
        rule: "Unsubscribe Mechanism Missing",
        description: "Marketing emails lack unsubscribe link as required by GDPR.",
        violationCode: `const sendEmail = (to, content) => {
  mailer.send({ to, html: content });
};`,
        fixedCode: `const sendEmail = (to, content) => {
  const unsubLink = generateUnsubscribeLink(to);
  const html = content + '<a href="' + unsubLink + '">Unsubscribe</a>';
  mailer.send({ to, html, headers: { 'List-Unsubscribe': unsubLink } });
};`,
        violationLines: [2],
      },
      {
        severity: "Medium",
        jurisdiction: "GDPR",
        rule: "Email Tracking Consent",
        description: "Pixel tracking in emails without user consent.",
        violationCode: `const html = content + '<img src="/track/' + campaignId + '" />';`,
        fixedCode: `const html = hasTrackingConsent(to) 
  ? content + '<img src="/track/' + campaignId + '" />'
  : content;`,
        violationLines: [1],
      },
      {
        severity: "Low",
        jurisdiction: "GDPR",
        rule: "Data Controller Identification",
        description: "Email footer missing data controller identification.",
        violationCode: `const footer = '<p>Thanks for reading!</p>';`,
        fixedCode: `const footer = '<p>Thanks for reading!</p>' +
  '<p>Data Controller: CompanyName Ltd, Address, DPO: dpo@company.com</p>';`,
        violationLines: [1],
      },
    ],
  },
  {
    id: 8,
    timestamp: "2024-01-15 12:55:00",
    file: "src/session.js",
    findings: 2,
    severity: { critical: 1, high: 1, medium: 0, low: 0 },
    jurisdictions: ["SOC2", "HIPAA"],
    details: [
      {
        severity: "Critical",
        jurisdiction: "SOC2",
        rule: "Session Token Security",
        description: "Session tokens transmitted without secure flag.",
        violationCode: `res.cookie('session', token, { httpOnly: true });`,
        fixedCode: `res.cookie('session', token, { httpOnly: true, secure: true, sameSite: 'strict' });`,
        violationLines: [1],
      },
      {
        severity: "High",
        jurisdiction: "HIPAA",
        rule: "Session Timeout Policy",
        description: "No automatic session timeout for PHI access.",
        violationCode: `const session = createSession({ userId });`,
        fixedCode: `const session = createSession({ userId, maxAge: 15 * 60 * 1000, idleTimeout: 5 * 60 * 1000 });`,
        violationLines: [1],
      },
    ],
  },
  {
    id: 9,
    timestamp: "2024-01-15 12:40:00",
    file: "src/upload.js",
    findings: 2,
    severity: { critical: 0, high: 0, medium: 2, low: 0 },
    jurisdictions: ["DPDP India", "GDPR"],
    details: [
      {
        severity: "Medium",
        jurisdiction: "DPDP India",
        rule: "Purpose Limitation",
        description: "File uploads used beyond stated purpose without consent.",
        violationCode: `const upload = multer({ dest: '/uploads/' });
app.post('/upload', upload.single('file'), processForML);`,
        fixedCode: `const upload = multer({ dest: '/uploads/' });
app.post('/upload', upload.single('file'), validatePurpose, processForML);`,
        violationLines: [2],
      },
      {
        severity: "Medium",
        jurisdiction: "GDPR",
        rule: "File Metadata Stripping",
        description: "Uploaded files retain EXIF/metadata containing personal information.",
        violationCode: `const saveFile = (file) => {
  fs.writeFileSync(path.join('/uploads', file.name), file.data);
};`,
        fixedCode: `const saveFile = (file) => {
  const stripped = stripMetadata(file.data);
  fs.writeFileSync(path.join('/uploads', file.name), stripped);
};`,
        violationLines: [2],
      },
    ],
  },
];

export const dependencyResults = [
  { name: "get", status: "Safe", version: "1.2.3", lastChecked: "Nov 10, 2023 19:34:37 EST" },
  { name: "package-name", status: "Safe", version: "3.0.1", lastChecked: "Nov 10, 2023 19:34:23 EST" },
  { name: "package-manager", status: "Safe", version: "2.1.0", lastChecked: "Aug 10, 2023 19:31:33 EST" },
  { name: "package", status: "Safe", version: "5.0.2", lastChecked: "Aug 10, 2023 10:31:33 EST" },
  { name: "package-installer", status: "Blocked", version: "1.0.0-rc1", lastChecked: "Nov 10, 2023 10:34:33 EST" },
  { name: "package-cache", status: "Safe", version: "4.2.1", lastChecked: "Nov 10, 2023 10:34:33 EST" },
  { name: "port", status: "Safe", version: "2.0.0", lastChecked: "Nov 10, 2023 10:34:33 EST" },
];

export const reportsData = [
  {
    id: 1,
    name: "GDPR Compliance Audit",
    date: "Jan 15, 2024",
    jurisdictions: ["GDPR"],
    findingsSummary: { critical: 2, high: 4, medium: 6, low: 3 },
    status: "Completed",
  },
  {
    id: 2,
    name: "Full Stack Security Review",
    date: "Jan 14, 2024",
    jurisdictions: ["GDPR", "SOC2", "HIPAA"],
    findingsSummary: { critical: 1, high: 3, medium: 8, low: 5 },
    status: "Completed",
  },
  {
    id: 3,
    name: "DPDP India Assessment",
    date: "Jan 13, 2024",
    jurisdictions: ["DPDP India"],
    findingsSummary: { critical: 0, high: 2, medium: 4, low: 2 },
    status: "Completed",
  },
  {
    id: 4,
    name: "HIPAA Compliance Check",
    date: "Jan 12, 2024",
    jurisdictions: ["HIPAA"],
    findingsSummary: { critical: 1, high: 1, medium: 3, low: 1 },
    status: "In Progress",
  },
  {
    id: 5,
    name: "SOC2 Type II Readiness",
    date: "Jan 11, 2024",
    jurisdictions: ["SOC2"],
    findingsSummary: { critical: 0, high: 2, medium: 5, low: 4 },
    status: "Completed",
  },
  {
    id: 6,
    name: "Multi-Jurisdiction Scan",
    date: "Jan 10, 2024",
    jurisdictions: ["GDPR", "DPDP India", "HIPAA", "SOC2"],
    findingsSummary: { critical: 3, high: 7, medium: 12, low: 8 },
    status: "Completed",
  },
  {
    id: 7,
    name: "Weekly Compliance Summary",
    date: "Jan 9, 2024",
    jurisdictions: ["GDPR", "SOC2"],
    findingsSummary: { critical: 0, high: 1, medium: 3, low: 6 },
    status: "Completed",
  },
];

export const pricingPlans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Get started with basic compliance scanning",
    features: [
      "10 scans/month",
      "1 jurisdiction",
      "Basic findings report",
      "Community support",
      "Email notifications",
    ],
    cta: "Get Started Free",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$99",
    period: "/month",
    description: "For teams serious about compliance",
    features: [
      "Unlimited scans",
      "All jurisdictions (GDPR, HIPAA, SOC2, DPDP)",
      "Advanced analytics dashboard",
      "Priority support",
      "PDF report export",
      "Dependency scanning (SafeDep)",
      "CI/CD integration",
      "Slack notifications",
    ],
    cta: "Start Pro Trial",
    highlighted: true,
    badge: "Popular",
  },
  {
    name: "Enterprise",
    price: "$5,000",
    period: "/year",
    description: "Complete compliance automation",
    features: [
      "Everything in Pro",
      "Full audit trail",
      "Custom jurisdiction rules",
      "SSO / SAML integration",
      "Dedicated account manager",
      "SLA guarantee (99.9%)",
      "On-premise deployment option",
      "Security whitepaper generation",
      "Custom API access",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
];
