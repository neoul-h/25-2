// db.js
// MySQL 연결 풀을 생성하는 파일
// 모든 컨트롤러에서 이 pool을 통해 DB에 접근한다.

const mysql = require('mysql2/promise');
const dotenv = require('dotenv');

dotenv.config(); // .env 파일 읽기

// 커넥션 풀 생성
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'minigit_db',

  // 🔑 한글 깨짐 방지 핵심 옵션
  charset: 'utf8mb4',

  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
});

module.exports = pool;
