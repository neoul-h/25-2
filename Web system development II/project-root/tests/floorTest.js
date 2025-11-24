// tests/floorTest.js
const { sequelize } = require('../models');
const {
  getFloorsByBuilding,
  createFloor,
} = require('../controllers/floorController');

async function runFloorTests() {
  try {
    console.log('🔍 DB 연결 시도...');
    await sequelize.authenticate();
    console.log('✅ DB 연결 성공');

    const testBuildingId = 1; // 갈멜관 같은 실제 존재하는 buildingId 사용

    console.log('\n[1] 층 생성 테스트');
    const newFloor = await createFloor(testBuildingId, {
      floorNumber: 9,
      name: '테스트층',
    });
    console.log('➤ 생성된 층 ID:', newFloor.id);

    console.log('\n[2] 건물별 층 목록 조회 테스트');
    const floors = await getFloorsByBuilding(testBuildingId);
    console.log('➤ 층 개수:', floors.length);

    console.log('\n✅ floorController 핵심 API 테스트 완료');
  } catch (err) {
    console.error('❌ 테스트 중 에러 발생:', err);
  } finally {
    await sequelize.close();
    console.log('🔚 DB 연결 종료');
  }
}

runFloorTests();
