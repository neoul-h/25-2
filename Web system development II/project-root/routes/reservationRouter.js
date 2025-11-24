// routes/reservationRouter.js
const express = require('express');
const router = express.Router();

const {
  getReservationsByRoom,
  getReservationById,
  createReservation,
  updateReservation,
  setReservationStatus,
  deleteReservation,
} = require('../controllers/reservationController');

// POST /rooms/:roomId/reservations - 예약 생성
router.post('/room/:roomId', async (req, res) => {
  try {
    const reservation = await createReservation(req.params.roomId, req.body);
    res.status(201).json({ success: true, data: reservation });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /rooms/:roomId/reservations - 방별 예약 목록
router.get('/room/:roomId', async (req, res) => {
  try {
    const reservations = await getReservationsByRoom(req.params.roomId);
    res.json({ success: true, data: reservations });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// GET /reservations/:id - 예약 상세
router.get('/:id', async (req, res) => {
  try {
    const reservation = await getReservationById(req.params.id);
    if (!reservation) {
      return res.status(404).json({ success: false, message: '예약을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: reservation });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /reservations/:id - 예약 내용 수정
router.patch('/:id', async (req, res) => {
  try {
    const reservation = await updateReservation(req.params.id, req.body);
    if (!reservation) {
      return res.status(404).json({ success: false, message: '예약을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: reservation });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /reservations/:id/approve - 승인
router.patch('/:id/approve', async (req, res) => {
  try {
    const reservation = await setReservationStatus(req.params.id, 'approved');
    if (!reservation) {
      return res.status(404).json({ success: false, message: '예약을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: reservation });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /reservations/:id/reject - 거절
router.patch('/:id/reject', async (req, res) => {
  try {
    const reservation = await setReservationStatus(req.params.id, 'rejected');
    if (!reservation) {
      return res.status(404).json({ success: false, message: '예약을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: reservation });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// PATCH /reservations/:id/cancel - 취소
router.patch('/:id/cancel', async (req, res) => {
  try {
    const reservation = await setReservationStatus(req.params.id, 'canceled');
    if (!reservation) {
      return res.status(404).json({ success: false, message: '예약을 찾을 수 없습니다.' });
    }
    res.json({ success: true, data: reservation });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

// DELETE /reservations/:id - 삭제
router.delete('/:id', async (req, res) => {
  try {
    const ok = await deleteReservation(req.params.id);
    if (!ok) {
      return res.status(404).json({ success: false, message: '예약을 찾을 수 없습니다.' });
    }
    res.json({ success: true, message: '삭제 완료' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, message: '서버 에러' });
  }
});

module.exports = router;
