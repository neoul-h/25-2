// tests/roomTest.js
const { sequelize } = require('../models');
const {
  createRoom,
  getRoomsByFloor,
  getRoomById,
} = require('../controllers/roomController');

async function runRoomTests() {
  try {
    console.log('🔍 DB 연결 시도...');
    await sequelize.authenticate();
    console.log('✅ DB 연결 성공');

    const testFloorId = 1; // 실제 존재하는 floorId 사용 (갈멜관 1층 등)

    console.log('\n[1] 방 생성 테스트');
    const newRoom = await createRoom(testFloorId, {
      name: '테스트룸',
      type: 'classroom',
      capacity: 10,
    });
    console.log('➤ 생성된 방 ID:', newRoom.id);

    console.log('\n[2] 층별 방 목록 테스트');
    const rooms = await getRoomsByFloor(testFloorId);
    console.log('➤ 층 내 방 개수:', rooms.length);

    console.log('\n[3] 방 상세 조회 테스트');
    const found = await getRoomById(newRoom.id);
    console.log('➤ 조회된 방 이름:', found ? found.name : '없음');

    console.log('\n✅ roomController 핵심 API 테스트 완료');
  } catch (err) {
    console.error('❌ 테스트 중 에러 발생:', err);
  } finally {
    await sequelize.close();
    console.log('🔚 DB 연결 종료');
  }
}

runRoomTests();
