const request = require('supertest');
const { makePoolMock } = require('./utils');

// ✅ db 모듈을 테스트마다 원하는 동작으로 바꾸기 위해 jest mock
jest.mock('../db', () => ({
  getConnection: jest.fn(),
}));

const pool = require('../db');
const app = require('../server');

describe('Auth Router (/auth)', () => {
  test('POST /auth/register - 회원가입 성공', async () => {
    const { pool: poolMock } = makePoolMock([
      // username 중복 체크
      [[]],
      // INSERT users
      [{ insertId: 1 }],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .post('/auth/register')
      .send({ username: 'alice', password: 'pw1234', name: 'Alice' });

    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('message', '회원가입 성공');
    expect(res.body.user).toMatchObject({ id: 1, username: 'alice', name: 'Alice' });
  });

  test('POST /auth/login - 로그인 성공 (token 반환)', async () => {
    const bcrypt = require('bcrypt');
    const hash = await bcrypt.hash('pw1234', 10);

    const { pool: poolMock } = makePoolMock([
      // SELECT user
      [[{ id: 1, username: 'alice', name: 'Alice', password_hash: hash, password: null }]],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .post('/auth/login')
      .send({ username: 'alice', password: 'pw1234' });

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('token');
    expect(res.body).toHaveProperty('user');
    expect(res.body.user).toMatchObject({ id: 1, username: 'alice', name: 'Alice' });
  });
});
