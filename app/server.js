const express = require('express');
const session = require('express-session');
const cookieParser = require('cookie-parser');
const path = require('path');
require('dotenv').config();

const { pool, query } = require('./src/config/database');
const runSeed = require('./src/database/seeder');
const { attachUser } = require('./src/middleware/auth');

const authRoutes = require('./src/routes/authRoutes');
const jobRoutes = require('./src/routes/jobRoutes');
const candidateRoutes = require('./src/routes/candidateRoutes');
const recruiterRoutes = require('./src/routes/recruiterRoutes');
const adminRoutes = require('./src/routes/adminRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// View engine setup
app.set('views', path.join(__dirname, 'src/views'));
app.set('view engine', 'ejs');

// Body parsers
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Static assets
app.use(express.static(path.join(__dirname, 'public')));

// Session configuration
app.use(session({
  secret: process.env.SESSION_SECRET || 'jobboard_super_secret_session_key_2026',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 1000 * 60 * 60 * 24, // 24 hours
    httpOnly: true,
    sameSite: 'lax',
    secure: process.env.NODE_ENV === 'production' && process.env.COOKIE_SECURE === 'true'
  }
}));

// Request Logger (Structured for Promtail/Loki)
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    const logLine = `[webapp] ${req.ip || req.connection.remoteAddress} - "${req.method} ${req.originalUrl} HTTP/${req.httpVersion}" ${res.statusCode} ${duration}ms`;
    if (res.statusCode >= 500) {
      console.error(`ERROR: ${logLine}`);
    } else if (res.statusCode >= 400) {
      console.warn(`WARN: ${logLine}`);
    } else {
      console.log(`INFO: ${logLine}`);
    }
  });
  next();
});

// Attach user session to all views
app.use(attachUser);

// Health check endpoint for Docker & Kubernetes
app.get('/health', async (req, res) => {
  try {
    await query('SELECT 1');
    res.status(200).json({ status: 'UP', database: 'connected', timestamp: new Date().toISOString() });
  } catch (err) {
    console.error('Health check database error:', err.message);
    res.status(503).json({ status: 'DOWN', database: 'disconnected', error: err.message });
  }
});

// Prometheus Metrics endpoint
app.get('/metrics', async (req, res) => {
  try {
    const jobs = await query("SELECT COUNT(*) as total FROM jobs");
    const users = await query("SELECT COUNT(*) as total FROM users");
    const apps = await query("SELECT COUNT(*) as total FROM applications");
    const jobCount = (jobs && jobs[0]) ? jobs[0].total : 0;
    const userCount = (users && users[0]) ? users[0].total : 0;
    const appCount = (apps && apps[0]) ? apps[0].total : 0;

    res.set('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
    res.send(`# HELP jobboard_up Status of Job Board web application
# TYPE jobboard_up gauge
jobboard_up 1
# HELP jobboard_jobs_total Total job postings in system
# TYPE jobboard_jobs_total gauge
jobboard_jobs_total ${jobCount}
# HELP jobboard_users_total Total registered users
# TYPE jobboard_users_total gauge
jobboard_users_total ${userCount}
# HELP jobboard_applications_total Total submitted applications
# TYPE jobboard_applications_total gauge
jobboard_applications_total ${appCount}
`);
  } catch (err) {
    console.error('Metrics calculation error:', err.message);
    res.set('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
    res.status(500).send('jobboard_up 0\n');
  }
});

// Custom error trigger endpoint for testing Loki LogQL queries
app.get('/trigger-error', (req, res) => {
  console.error('[webapp] ERROR: Exception triggered manually for testing Loki LogQL queries!');
  res.status(500).send('Manual 500 Error Generated for Loki LogQL Verification');
});

// Register Routes
app.use('/', jobRoutes);
app.use('/auth', authRoutes);
app.use('/candidate', candidateRoutes);
app.use('/recruiter', recruiterRoutes);
app.use('/admin', adminRoutes);

// 404 Handler
app.use((req, res) => {
  res.status(404).render('partials/404', { title: '404 - Không tìm thấy trang' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('[webapp] Uncaught Exception:', err.stack);
  res.status(500).send('Đã xảy ra lỗi máy chủ nội bộ. Vui lòng thử lại sau.');
});

// Start Server and run Seeder in background
app.listen(PORT, '0.0.0.0', async () => {
  console.log(`[webapp] Job Board Server running on port ${PORT}`);
  console.log(`[webapp] Environment: ${process.env.NODE_ENV || 'development'}`);
  
  // Run seeder automatically if DB is ready
  try {
    await runSeed();
    console.log('[webapp] Database initialization & seeding completed.');
  } catch (err) {
    console.warn('[webapp] Background seeding note:', err.message);
  }
});
