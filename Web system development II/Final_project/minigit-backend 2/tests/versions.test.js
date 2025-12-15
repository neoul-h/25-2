const request = require('supertest');
const { makeToken, authHeader, makePoolMock } = require('./utils');

jest.mock('../db', () => ({ getConnection: jest.fn() }));

jest.mock('../controllers/versionController', () => ({
  getVersionsByDocument: (req, res) => res.json({ versions: [{ id: 1, version_no: 1 }] }),
  applyVersion: (req, res) => res.status(200).json({ message: 'version applied' }),
  getVersionById: (req, res) => res.status(200).json({ version: { id: Number(req.params.id) } }),
  deleteVersion: (req, res) => res.status(200).json({ message: 'version deleted' }),
}));

const pool = require('../db');
const app = require('../server');

describe('Versions Router (/versions)', () => {
  test('GET /versions/document/:documentId - 토큰 없으면 401', async () => {
    const res = await request(app).get('/versions/document/1');
    expect(res.status).toBe(401);
  });

  test('GET /versions/document/:documentId - 멤버면 200', async () => {
    const token = makeToken({ id: 2 });

    // requireProjectMemberByDocumentId:
    // 1) documents에서 project_id 조회
    // 2) project_members에서 role 조회
    const { pool: poolMock } = makePoolMock([
      [[{ project_id: 11 }]],
      [[{ role: 'member' }]],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .get('/versions/document/1')
      .set(authHeader(token));

    expect(res.status).toBe(200);
    expect(res.body.versions[0]).toMatchObject({ id: 1, version_no: 1 });
  });
});
