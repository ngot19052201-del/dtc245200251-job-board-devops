const mysql = require('mysql2/promise');
require('dotenv').config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'mysql',
  port: parseInt(process.env.DB_PORT || '3306', 10),
  user: process.env.DB_USER || 'jobuser',
  password: process.env.DB_PASSWORD || 'JobPass@2026_Secure',
  database: process.env.DB_NAME || 'jobboard_db',
  waitForConnections: true,
  connectionLimit: 15,
  queueLimit: 0,
  charset: 'utf8mb4'
});

// Helper execute with retry for initial database booting
async function query(sql, params = []) {
  const [rows, fields] = await pool.execute(sql, params);
  return rows;
}

module.exports = {
  pool,
  query
};
