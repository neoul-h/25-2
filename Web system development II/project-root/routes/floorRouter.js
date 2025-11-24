// routes/floorRouter.js
const express = require('express');
const router = express.Router();

const {
  getFloorsByBuilding,
  getFloorById,
  createFloor,
  updateFloor,
  deleteFloor,
} = require('../controllers/floorController');

// GET /buildings/:buildingId/floors - 건물별 층 목록
router.get('/building/:buildingId', async (req, res) => {
  try {
    const floors = await getFloorsByBuilding(req.params.buildingId);
    res.json({ success: true, data: floors });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /floors/:id - 층 상세
router.get('/:id', async (req, res) => {
  try {
    const floor = await getFloorById(req.params.id);
    if (!floor) {
      return res.status(404).json({ success: false, message: '층을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: floor });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// POST /buildings/:buildingId/floors - 층 생성
router.post('/building/:buildingId', async (req, res) => {
  try {
    const floor = await createFloor(req.params.buildingId, req.body);
    res.status(201).json({ success: true, data: floor });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /floors/:id - 층 수정
router.patch('/:id', async (req, res) => {
  try {
    const floor = await updateFloor(req.params.id, req.body);
    if (!floor) {
      return res.status(404).json({ success: false, message: '층을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: floor });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// DELETE /floors/:id - 층 삭제
router.delete('/:id', async (req, res) => {
  try {
    const ok = await deleteFloor(req.params.id);
    if (!ok) {
      return res.status(404).json({ success: false, message: '층을 찾을 수 없습니다.' });
    }
    res.json({ success: true, message: '삭제 완료' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;
