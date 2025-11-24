// controllers/malfunctionController.js
const { Malfunction } = require('../models');

// 전체 고장 목록 (필터: status, severity)
async function getAllMalfunctions(filter = {}) {
  const where = {};
  if (filter.status) where.status = filter.status;
  if (filter.severity) where.severity = filter.severity;

  const list = await Malfunction.findAll({
    where,
    order: [['reportedAt', 'DESC']],
  });
  return list;
}

// 방별 고장 목록
async function getMalfunctionsByRoom(roomId) {
  const list = await Malfunction.findAll({
    where: { roomId },
    order: [['reportedAt', 'DESC']],
  });
  return list;
}

// 상세 조회
async function getMalfunctionById(id) {
  const m = await Malfunction.findByPk(id);
  return m;
}

// 고장 신고 생성
async function createMalfunction(roomId, data) {
  const { facilityId, reportedBy, description, severity } = data;
  const m = await Malfunction.create({
    roomId,
    facilityId: facilityId || null,
    reportedBy: reportedBy || null,
    description,
    severity: severity || 'low',
    status: 'open',
    reportedAt: new Date(),
  });
  return m;
}

// 고장 수정 (설명/심각도/상태 변경)
async function updateMalfunction(id, data) {
  const m = await Malfunction.findByPk(id);
  if (!m) return null;

  const { description, severity, status, resolvedAt } = data;
  await m.update({
    description: description ?? m.description,
    severity: severity ?? m.severity,
    status: status ?? m.status,
    resolvedAt: resolvedAt ?? m.resolvedAt,
  });

  return m;
}

// 삭제
async function deleteMalfunction(id) {
  const m = await Malfunction.findByPk(id);
  if (!m) return false;
  await m.destroy();
  return true;
}

module.exports = {
  getAllMalfunctions,
  getMalfunctionsByRoom,
  getMalfunctionById,
  createMalfunction,
  updateMalfunction,
  deleteMalfunction,
};
