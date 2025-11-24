// controllers/reservationController.js
const { Reservation } = require('../models');

// 방별 예약 목록
async function getReservationsByRoom(roomId) {
  const reservations = await Reservation.findAll({
    where: { roomId },
    order: [['startTime', 'ASC']],
  });
  return reservations;
}

// 예약 상세
async function getReservationById(id) {
  const reservation = await Reservation.findByPk(id);
  return reservation;
}

// 예약 생성
async function createReservation(roomId, data) {
  const { userId, purpose, startTime, endTime } = data;
  const reservation = await Reservation.create({
    roomId,
    userId,
    purpose,
    startTime,
    endTime,
    status: 'pending',
  });
  return reservation;
}

// 예약 수정 (시간/목적)
async function updateReservation(id, data) {
  const reservation = await Reservation.findByPk(id);
  if (!reservation) return null;

  const { purpose, startTime, endTime } = data;
  await reservation.update({
    purpose: purpose ?? reservation.purpose,
    startTime: startTime ?? reservation.startTime,
    endTime: endTime ?? reservation.endTime,
  });
  return reservation;
}

// 상태 변경
async function setReservationStatus(id, status) {
  const reservation = await Reservation.findByPk(id);
  if (!reservation) return null;
  await reservation.update({ status });
  return reservation;
}

// 삭제
async function deleteReservation(id) {
  const reservation = await Reservation.findByPk(id);
  if (!reservation) return false;
  await reservation.destroy();
  return true;
}

module.exports = {
  getReservationsByRoom,
  getReservationById,
  createReservation,
  updateReservation,
  setReservationStatus,
  deleteReservation,
};
