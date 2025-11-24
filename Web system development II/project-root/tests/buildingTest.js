// tests/buildingTest.js
const { sequelize } = require('../models');
const {
  getAllBuildings,
  createBuilding,
  getBuildingById,
} = require('../controllers/buildingController');

async function runBuildingTests() {
  try {
    console.log('🔍 DB 연결 시도...');
    await sequelize.authenticate();
    console.log('✅ DB 연결 성공');

    console.log('\n[1] 건물 생성 테스트');
    const newBuilding = await createBuilding({
      name: '테스트관',
      code: 'TEST',
      description: '테스트용 건물입니다.',
    });
    console.log('➤ 생성된 건물 ID:', newBuilding.id);

    console.log('\n[2] 건물 목록 조회 테스트');
    const buildings = await getAllBuildings();
    console.log('➤ 건물 개수:', buildings.length);

    console.log('\n[3] 특정 건물 조회 테스트');
    const found = await getBuildingById(newBuilding.id);
    console.log('➤ 조회된 건물 이름:', found ? found.name : '없음');

    console.log('\n✅ buildingController 핵심 API 테스트 완료');
  } catch (err) {
    console.error('❌ 테스트 중 에러 발생:', err);
  } finally {
    await sequelize.close();
    console.log('🔚 DB 연결 종료');
  }
}

runBuildingTests();
