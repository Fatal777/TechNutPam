/**
 * ComplianceShield Demo: Intentionally Insecure Express App
 * ==========================================================
 * This file exists to demonstrate ComplianceShield's scan_code tool.
 * It contains 8 deliberate compliance violations across GDPR and DPDP.
 *
 * USE IN DEMO:
 *   1. Call scan_code with this file's contents
 *   2. Show the 8 violations returned
 *   3. Call get_fixes to auto-remediate
 *   4. Show the clean diff
 *
 * DO NOT deploy this code. It is intentionally broken for demo purposes.
 */

const express = require('express');
const mysql = require('mysql');
const app = express();
app.use(express.json());

// VIOLATION 1 [GDPR-7 / SOC2-C1.1]: Hardcoded database password
const DB_PASSWORD = "admin123";
const DB_HOST = "us-east-1.rds.amazonaws.com";  // VIOLATION 2 [DPDP-1]: Non-Indian server

const db = mysql.createConnection({
  host: DB_HOST,
  user: 'root',
  password: DB_PASSWORD,
  database: 'users'
});

app.post('/register', (req, res) => {
  const { name, email, ssn, phone, dob } = req.body;

  // VIOLATION 3 [GDPR-1 / HIPAA-1]: PII logged to console
  console.log(`New user: ${name}, ${email}, SSN: ${ssn}, DOB: ${dob}`);

  // VIOLATION 4 [GDPR-3 / DPDP-3]: No consent collected before processing
  // No consent check here — data is processed immediately

  // VIOLATION 5 [GDPR-5]: SSN and DOB collected but not needed for registration
  // VIOLATION 6 [GDPR-8 / SOC2-PI1.2]: SQL injection via string interpolation
  const query = `INSERT INTO users VALUES ('${name}', '${email}', '${ssn}', '${phone}')`;
  db.query(query);

  // VIOLATION 7 [GDPR-4 / DPDP-3]: No right-to-deletion endpoint anywhere in app

  // VIOLATION 8 [GDPR-2]: Data stored without encryption (plaintext SSN in DB)

  res.json({ success: true, userData: { name, email, ssn } }); // Also exposes PII in response
});

app.get('/users', (req, res) => {
  // VIOLATION [SOC2-CC6.1]: No authentication check — anyone can list all users
  db.query('SELECT * FROM users', (err, results) => {
    res.json(results);
  });
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');  // HTTP, not HTTPS [SOC2-CC6.7]
});
