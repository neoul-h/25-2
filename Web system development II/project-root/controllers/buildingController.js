// controllers/buildingController.js
const { Building } = require('../models');

// 전체 건물 조회
async function getAllBuildings() {
  const buildings = await Building.findAll();
  return buildings;
}

// 특정 건물 조회
async function getBuildingById(id) {
  const building = await Building.findByPk(id);
  return building;
}

// 건물 생성
async function createBuilding(data) {
  const { name, code, description } = data;
  const building = await Building.create({ name, code, description });
  return building;
}

// 건물 수정
async function updateBuilding(id, data) {
  const building = await Building.findByPk(id);
  if (!building) return null;

  const { name, code, description } = data;
  await building.update({ name, code, description });
  return building;
}

// 건물 삭제
async function deleteBuilding(id) {
  const building = await Building.findByPk(id);
  if (!building) return false;
  await building.destroy();
  return true;
}

module.exports = {
  getAllBuildings,
  getBuildingById,
  createBuilding,
  updateBuilding,
  deleteBuilding,
};
