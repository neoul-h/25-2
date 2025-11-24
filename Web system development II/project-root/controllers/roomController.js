// controllers/roomController.js
const { Room } = require('../models');

// 층별 방 목록
async function getRoomsByFloor(floorId) {
  const rooms = await Room.findAll({
    where: { floorId },
    order: [['name', 'ASC']],
  });
  return rooms;
}

// 필터 기반 전체 방 조회 (옵션: buildingId/floorId/type)
async function getAllRooms(filter = {}) {
  const where = {};

  if (filter.floorId) {
    where.floorId = filter.floorId;
  }
  if (filter.type) {
    where.type = filter.type;
  }

  const rooms = await Room.findAll({ where });
  return rooms;
}

// 방 상세
async function getRoomById(id) {
  const room = await Room.findByPk(id);
  return room;
}

// 방 생성
async function createRoom(floorId, data) {
  const { name, type, capacity, isAvailable } = data;
  const room = await Room.create({
    floorId,
    name,
    type: type || 'etc',
    capacity: capacity || null,
    isAvailable: isAvailable !== undefined ? isAvailable : true,
  });
  return room;
}

// 방 수정
async function updateRoom(id, data) {
  const room = await Room.findByPk(id);
  if (!room) return null;

  const { name, type, capacity, isAvailable } = data;
  await room.update({
    name: name ?? room.name,
    type: type ?? room.type,
    capacity: capacity ?? room.capacity,
    isAvailable: isAvailable ?? room.isAvailable,
  });

  return room;
}

// 방 삭제
async function deleteRoom(id) {
  const room = await Room.findByPk(id);
  if (!room) return false;
  await room.destroy();
  return true;
}

module.exports = {
  getRoomsByFloor,
  getAllRooms,
  getRoomById,
  createRoom,
  updateRoom,
  deleteRoom,
};
