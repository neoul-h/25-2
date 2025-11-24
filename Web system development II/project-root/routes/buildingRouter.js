// routes/buildingRouter.js
const express = require('express');
const router = express.Router();

const {
  getAllBuildings,
  getBuildingById,
  createBuilding,
  updateBuilding,
  deleteBuilding,
} = require('../controllers/buildingController');

// GET /buildings - 건물 목록
router.get('/', async (req, res) => {
  try {
    const buildings = await getAllBuildings();
    res.json({ success: true, data: buildings });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /buildings/:id - 건물 상세
router.get('/:id', async (req, res) => {
  try {
    const building = await getBuildingById(req.params.id);
    if (!building) {
      return res.status(404).json({ success: false, message: '건물을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: building });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// POST /buildings - 건물 생성
router.post('/', async (req, res) => {
  try {
    const building = await createBuilding(req.body);
    res.status(201).json({ success: true, data: building });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /buildings/:id - 건물 수정
router.patch('/:id', async (req, res) => {
  try {
    const building = await updateBuilding(req.params.id, req.body);
    if (!building) {
      return res.status(404).json({ success: false, message: '건물을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: building });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// DELETE /buildings/:id - 건물 삭제
router.delete('/:id', async (req, res) => {
  try {
    const ok = await deleteBuilding(req.params.id);
    if (!ok) {
      return res.status(404).json({ success: false, message: '건물을 찾을 수 없습니다.' });
    }
    res.json({ success: true, message: '삭제 완료' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;
