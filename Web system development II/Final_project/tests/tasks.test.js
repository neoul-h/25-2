const request = require('supertest');
const { makeToken, authHeader, makePoolMock } = require('./utils');

jest.mock('../db', () => ({ getConnection: jest.fn() }));

// ⚠️ 라우터 로딩 시 routes/tasks.js가 여러 핸들러를 참조하므로,
// 테스트에서 일부만 mock 하면 "callback function got Undefined" 에러가 납니다.
// 그래서 라우터에서 쓰는 핸들러를 전부 stub로 제공합니다.
jest.mock('../controllers/taskController', () => ({
  createTask: (req, res) => res.status(201).json({ message: 'task created', task: { id: 99 } }),
  getTasksByProject: (req, res) => res.status(200).json({ tasks: [] }),
  getTaskById: (req, res) => res.status(200).json({ task: { id: Number(req.params.id) } }),
  updateTask: (req, res) => res.status(200).json({ message: 'task updated' }),
  deleteTask: (req, res) => res.status(200).json({ message: 'task deleted' }),
}));

const pool = require('../db');
const app = require('../server');

describe('Tasks Router (/tasks)', () => {
  test('POST /tasks - 토큰 없으면 401', async () => {
    const res = await request(app).post('/tasks').send({ project_id: 1, title: 't' });
    expect(res.status).toBe(401);
  });

  test('POST /tasks - 멤버면 201', async () => {
    const token = makeToken({ id: 5 });

    // requireProjectMemberByProjectId: project_members 조회
    const { pool: poolMock } = makePoolMock([
      [[{ role: 'member' }]],
    ]);
    pool.getConnection.mockImplementation(poolMock.getConnection);

    const res = await request(app)
      .post('/tasks')
      .set(authHeader(token))
      .send({ project_id: 1, title: 'task1' });

    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ message: 'task created' });
  });
});
