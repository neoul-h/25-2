const request = require('supertest');
const { makeToken, authHeader, makePoolMock } = require('./utils');

jest.mock('../db', () => ({
  getConnection: jest.fn(),
}));

// ✅ 컨트롤러는 라우터별 연결/권한 테스트 목적이므로 가볍게 mock
jest.mock('../controllers/documentController', () => ({
  // routes/documents.js에서 참조하는 핸들러를 전부 stub로 제공 (부분 mock 시 라우터 로딩 에러)
  getDocumentsByProject: (req, res) => res.json({ documents: [{ id: 1, title: 'doc' }] }),
  createDocument: (req, res) => res.status(201).json({ message: 'doc created', document: { id: 10 } }),
  getDocumentById: (req, res) => res.status(200).json({ document: { id: Number(req.params.id) }, versions: [] }),
  updateDocument: (req, res) => res.status(200).json({ message: 'doc updated' }),
  deleteDocument: (req, res) => res.status(200).json({ message: 'doc deleted' }),
}));

const pool = require('../db');
const app = require('../server');

describe('Documents Router (/documents)', () => {
  test('GET /documents/project/:projectId - 토큰 없으면 401', async () => {
    const res = await request(app).get('/documents/project/1');
    expect(res.status).toBe(401);
  });

  test('GET /documents/project/:projectId - 멤버면 200', async () => {
    const token = makeToken({ id: 3 });

    // requireProjectMemberByProjectId 에서 project_members 조회 1번
    const { pool: poolMock } = makePoolMock([
      [[{ role: 'member' }]],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .get('/documents/project/1')
      .set(authHeader(token));

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('documents');
    expect(res.body.documents[0]).toMatchObject({ id: 1, title: 'doc' });
  });
});
