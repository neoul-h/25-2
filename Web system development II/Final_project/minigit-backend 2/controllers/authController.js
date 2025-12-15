// controllers/authController.js
// 사용자 회원가입 / 로그인 / 조회 로직

const pool = require('../db');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const SALT_ROUNDS = 10;

// 회원가입
exports.register = async (req, res) => {
  try {
    const { username, password, name } = req.body;

    // 필수 값 체크
    if (!username || !password || !name) {
      return res.status(400).json({
        message: 'username, password, name은 필수입니다.',
      });
    }

    const conn = await pool.getConnection();
    try {
      // username 중복 체크
      const [existing] = await conn.query(
        'SELECT id FROM users WHERE username = ?',
        [username]
      );

      if (existing.length > 0) {
        return res.status(409).json({
          message: '이미 존재하는 사용자입니다.',
        });
      }

      // ✅ 비밀번호 해시
      const password_hash = await bcrypt.hash(password, SALT_ROUNDS);

      // DB 컬럼 호환 (password_hash 우선, 없으면 password)
      let result;
      try {
        const [r] = await conn.query(
          'INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)',
          [username, password_hash, name]
        );
        result = r;
      } catch (e) {
        const [r] = await conn.query(
          'INSERT INTO users (username, password, name) VALUES (?, ?, ?)',
          [username, password_hash, name]
        );
        result = r;
      }

      return res.status(201).json({
        message: '회원가입 성공',
        user: {
          id: result.insertId,
          username,
          name,
        },
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('register error:', err);
    res.status(500).json({
      message: '서버 오류',
      error: err.message,
    });
  }
};

// 로그인
exports.login = async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({
        message: 'username, password는 필수입니다.',
      });
    }

    const conn = await pool.getConnection();
    try {
      // ✅ password_hash 컬럼이 있든 없든 대응하기 위해 둘 다 SELECT
      const [rows] = await conn.query(
        'SELECT id, username, name, password, password_hash FROM users WHERE username = ?',
        [username]
      );

      if (rows.length === 0) {
        return res.status(401).json({
          message: '존재하지 않는 아이디입니다.',
        });
      }

      const user = rows[0];

      // ✅ 해시 우선 사용, 없으면 password 사용 (호환)
      const storedHash = user.password_hash || user.password;

      const looksHashed = typeof storedHash === 'string' && storedHash.startsWith('$2');

      let ok = false;
      if (looksHashed) ok = await bcrypt.compare(password, storedHash);
      else ok = storedHash === password;

      if (!ok) {
        return res.status(401).json({
          message: '비밀번호가 틀렸습니다.',
        });
      }

      // ✅ JWT 발급 (🔥 payload 키를 id로 통일)
      const secret = process.env.JWT_SECRET;
      if (!secret) {
        return res.status(500).json({
          message: '서버 설정 오류(JWT_SECRET 누락)',
        });
      }

      const payload = {
        id: user.id,
        username: user.username,
        name: user.name,
      };

      const token = jwt.sign(payload, secret, { expiresIn: '2h' });

      // ✅ 프론트가 기대하는 형태: { token, user }
      return res.json({
        token,
        user: payload,
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('login error:', err);
    res.status(500).json({
      message: '서버 오류',
      error: err.message,
    });
  }
};

// 사용자 목록 조회 (테스트용)
exports.getUsers = async (req, res) => {
  try {
    const conn = await pool.getConnection();
    try {
      const [rows] = await conn.query(
        'SELECT id, username, name, created_at FROM users'
      );
      res.json({ users: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getUsers error:', err);
    res.status(500).json({
      message: '서버 오류',
      error: err.message,
    });
  }
};
