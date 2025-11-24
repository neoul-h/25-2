// routes/roomRouter.js
const express = require('express');
const router = express.Router();

const {
  getRoomsByFloor,
  getAllRooms,
  getRoomById,
  createRoom,
  updateRoom,
  deleteRoom,
} = require('../controllers/roomController');

// GET /floors/:floorId/rooms - 층별 방 목록
router.get('/floor/:floorId', async (req, res) => {
  try {
    const rooms = await getRoomsByFloor(req.params.floorId);
    res.json({ success: true, data: rooms });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /rooms - 전체 방 (필터 가능)
router.get('/', async (req, res) => {
  try {
    const { floorId, type } = req.query;
    const rooms = await getAllRooms({ floorId, type });
    res.json({ success: true, data: rooms });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /rooms/:id - 방 상세
router.get('/:id', async (req, res) => {
  try {
    const room = await getRoomById(req.params.id);
    if (!room) {
      return res.status(404).json({ success: false, message: '방을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: room });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// POST /floors/:floorId/rooms - 방 생성
router.post('/floor/:floorId', async (req, res) => {
  try {
    const room = await createRoom(req.params.floorId, req.body);
    res.status(201).json({ success: true, data: room });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /rooms/:id - 방 수정
router.patch('/:id', async (req, res) => {
  try {
    const room = await updateRoom(req.params.id, req.body);
    if (!room) {
      return res.status(404).json({ success: false, message: '방을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: room });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// DELETE /rooms/:id - 방 삭제
router.delete('/:id', async (req, res) => {
  try {
    const ok = await deleteRoom(req.params.id);
    if (!ok) {
      return res.status(404).json({ success: false, message: '방을 찾을 수 없습니다.' });
    }
    res.json({ success: true, message: '삭제 완료' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;
