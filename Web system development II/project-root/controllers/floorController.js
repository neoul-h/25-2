// controllers/floorController.js
const { Floor } = require('../models');

// 특정 건물의 층 목록
async function getFloorsByBuilding(buildingId) {
  const floors = await Floor.findAll({
    where: { buildingId },
    order: [['floorNumber', 'ASC']],
  });
  return floors;
}

// 층 상세 조회
async function getFloorById(id) {
  const floor = await Floor.findByPk(id);
  return floor;
}

// 층 생성
async function createFloor(buildingId, data) {
  const { floorNumber, name } = data;
  const floor = await Floor.create({ buildingId, floorNumber, name });
  return floor;
}

// 층 수정
async function updateFloor(id, data) {
  const floor = await Floor.findByPk(id);
  if (!floor) return null;

  const { floorNumber, name } = data;
  await floor.update({ floorNumber, name });
  return floor;
}

// 층 삭제
async function deleteFloor(id) {
  const floor = await Floor.findByPk(id);
  if (!floor) return false;
  await floor.destroy();
  return true;
}

module.exports = {
  getFloorsByBuilding,
  getFloorById,
  createFloor,
  updateFloor,
  deleteFloor,
};
