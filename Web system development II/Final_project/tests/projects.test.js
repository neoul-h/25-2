const request = require('supertest');
const { makeToken, authHeader, makePoolMock } = require('./utils');

jest.mock('../db', () => ({
  getConnection: jest.fn(),
}));

const pool = require('../db');
const app = require('../server');

describe('Projects Router (/projects)', () => {
  test('GET /projects - 토큰 없으면 401', async () => {
    const res = await request(app).get('/projects');
    expect(res.status).toBe(401);
  });

  test('POST /projects - 생성 성공', async () => {
    const token = makeToken({ id: 7, username: 'u7', name: 'U7' });

    const { pool: poolMock } = makePoolMock([
      // INSERT projects
      [{ insertId: 10 }],
      // INSERT project_members
      [{}],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .post('/projects')
      .set(authHeader(token))
      .send({ name: 'My Project', description: 'desc' });

    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('message', '프로젝트 생성 성공');
    expect(res.body.project).toMatchObject({ id: 10, name: 'My Project', owner_id: 7 });
  });

  test('GET /projects - 내 프로젝트 목록 조회', async () => {
    const token = makeToken({ id: 7 });

    const { pool: poolMock } = makePoolMock([
      [[{ id: 10, name: 'My Project' }]],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .get('/projects')
      .set(authHeader(token));

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('projects');
    expect(res.body.projects[0]).toMatchObject({ id: 10, name: 'My Project' });
  });
});
