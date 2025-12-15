const jwt = require('jsonwebtoken');

function makeToken({ id = 1, username = 'tester', name = '테스터' } = {}) {
  const secret = process.env.JWT_SECRET;
  return jwt.sign({ id, username, name }, secret, { expiresIn: '1h' });
}

function authHeader(token) {
  return { Authorization: `Bearer ${token}` };
}

/**
 * mysql2/promise pool mock helper
 * - queue에 넣은 값이 conn.query() 호출 순서대로 resolve 됩니다.
 * - 각 항목은 mysql2의 query 반환 형태를 흉내 내서 [rows] 형태로 넣어주세요.
 */
function makePoolMock(queryQueue = []) {
  const query = jest.fn();
  for (const v of queryQueue) query.mockResolvedValueOnce(v);

  const conn = {
    query,
    beginTransaction: jest.fn().mockResolvedValue(undefined),
    commit: jest.fn().mockResolvedValue(undefined),
    rollback: jest.fn().mockResolvedValue(undefined),
    release: jest.fn(),
  };

  const pool = {
    getConnection: jest.fn().mockResolvedValue(conn),
  };

  return { pool, conn, query };
}

module.exports = { makeToken, authHeader, makePoolMock };
