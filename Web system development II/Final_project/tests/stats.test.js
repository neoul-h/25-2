const request = require('supertest');
const { makeToken, authHeader } = require('./utils');

jest.mock('../controllers/statsController', () => ({
  getTaskStatusStats: jest.fn((req, res) => res.status(200).json({ ok: true })),
  getDailyCommits: jest.fn((req, res) => res.status(200).json({ ok: true })),
  getDocumentHealth: jest.fn((req, res) => res.status(200).json({ ok: true })),
  getContributions: jest.fn((req, res) => res.status(200).json({ contributions: [] })
  ),
  // ✅ 여기 2개 추가!
  getProjectSummary: jest.fn((req, res) => res.status(200).json({ ok: true })),
  getUserProjectStats: jest.fn((req, res) => res.status(200).json({ ok: true })),
}));

const app = require('../server');

describe('Stats Router (/stats)', () => {
  test('GET /stats/project/:projectId/contributions - 토큰 없으면 401', async () => {
    const res = await request(app).get('/stats/project/1/contributions');
    expect(res.status).toBe(401);
  });

  test('GET /stats/project/:projectId/contributions - 토큰 있으면 200', async () => {
    const token = makeToken({ id: 1 });
    const res = await request(app)
      .get('/stats/project/1/contributions')
      .set(authHeader(token));
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('contributions');
  });
});
