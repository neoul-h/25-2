const request = require('supertest');
const { makeToken } = require('./utils');

jest.mock('../controllers/filesController', () => ({
  downloadVersionFile: (req, res) => res.status(200).send('ok'),
  inlineVersionFile: (req, res) => res.status(200).send('ok'),
}));

const app = require('../server');

describe('Files Router (/files)', () => {
  test('GET /files/version/:versionId - 토큰 없으면 401', async () => {
    const res = await request(app).get('/files/version/1');
    expect(res.status).toBe(401);
  });

  test('GET /files/version/:versionId - ?token=으로도 통과', async () => {
    const token = makeToken({ id: 1 });
    const res = await request(app).get(`/files/version/1?token=${token}`);
    expect(res.status).toBe(200);
    expect(res.text).toBe('ok');
  });
});
