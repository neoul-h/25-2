// tests/malfunctionTest.js
const { sequelize } = require('../models');
const {
  createMalfunction,
  getMalfunctionsByRoom,
  getAllMalfunctions,
} = require('../controllers/malfunctionController');

async function runMalfunctionTests() {
  try {
    console.log('🔍 DB 연결 시도...');
    await sequelize.authenticate();
    console.log('✅ DB 연결 성공');

    const testRoomId = 1; // 실제 roomId 사용

    console.log('\n[1] 고장 신고 생성 테스트');
    const m = await createMalfunction(testRoomId, {
      description: '테스트용 빔프로젝터 고장',
      severity: 'medium',
    });
    console.log('➤ 생성된 고장 ID:', m.id);

    console.log('\n[2] 방별 고장 목록 테스트');
    const listByRoom = await getMalfunctionsByRoom(testRoomId);
    console.log('➤ 해당 방 고장 개수:', listByRoom.length);

    console.log('\n[3] 전체 고장 목록(필터) 테스트');
    const listAll = await getAllMalfunctions({ severity: 'medium' });
    console.log('➤ medium 고장 개수:', listAll.length);

    console.log('\n✅ malfunctionController 핵심 API 테스트 완료');
  } catch (err) {
    console.error('❌ 테스트 중 에러 발생:', err);
  } finally {
    await sequelize.close();
    console.log('🔚 DB 연결 종료');
  }
}

runMalfunctionTests();
