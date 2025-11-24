// routes/malfunctionRouter.js
const express = require('express');
const router = express.Router();

const {
  getAllMalfunctions,
  getMalfunctionsByRoom,
  getMalfunctionById,
  createMalfunction,
  updateMalfunction,
  deleteMalfunction,
} = require('../controllers/malfunctionController');

// POST /rooms/:roomId/malfunctions - 고장 신고 생성
router.post('/room/:roomId', async (req, res) => {
  try {
    const m = await createMalfunction(req.params.roomId, req.body);
    res.status(201).json({ success: true, data: m });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /rooms/:roomId/malfunctions - 방별 고장 목록
router.get('/room/:roomId', async (req, res) => {
  try {
    const list = await getMalfunctionsByRoom(req.params.roomId);
    res.json({ success: true, data: list });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /malfunctions - 전체 고장 목록 (status/severity 필터)
router.get('/', async (req, res) => {
  try {
    const { status, severity } = req.query;
    const list = await getAllMalfunctions({ status, severity });
    res.json({ success: true, data: list });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /malfunctions/:id - 상세
router.get('/:id', async (req, res) => {
  try {
    const m = await getMalfunctionById(req.params.id);
    if (!m) {
      return res.status(404).json({ success: false, message: '고장 정보를 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: m });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /malfunctions/:id - 수정
router.patch('/:id', async (req, res) => {
  try {
    const m = await updateMalfunction(req.params.id, req.body);
    if (!m) {
      return res.status(404).json({ success: false, message: '고장 정보를 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: m });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// DELETE /malfunctions/:id - 삭제
router.delete('/:id', async (req, res) => {
  try {
    const ok = await deleteMalfunction(req.params.id);
    if (!ok) {
      return res.status(404).json({ success: false, message: '고장 정보를 찾을 수 없습니다.' });
    }
    res.json({ success: true, message: '삭제 완료' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;
