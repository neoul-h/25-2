// tests/reservationTest.js
const { sequelize } = require('../models');
const {
  createReservation,
  getReservationsByRoom,
  setReservationStatus,
} = require('../controllers/reservationController');

async function runReservationTests() {
  try {
    console.log('🔍 DB 연결 시도...');
    await sequelize.authenticate();
    console.log('✅ DB 연결 성공');

    const testRoomId = 1; // 실제 존재하는 roomId 사용
    const testUserId = 1; // user 미리 하나 만들어두면 좋음

    console.log('\n[1] 예약 생성 테스트');
    const r = await createReservation(testRoomId, {
      userId: testUserId,
      purpose: '테스트 예약',
      startTime: new Date(),
      endTime: new Date(Date.now() + 60 * 60 * 1000),
    });
    console.log('➤ 생성된 예약 ID:', r.id);

    console.log('\n[2] 방별 예약 목록 테스트');
    const list = await getReservationsByRoom(testRoomId);
    console.log('➤ 예약 개수:', list.length);

    console.log('\n[3] 예약 승인 상태 변경 테스트');
    const approved = await setReservationStatus(r.id, 'approved');
    console.log('➤ 변경된 상태:', approved.status);

    console.log('\n✅ reservationController 핵심 API 테스트 완료');
  } catch (err) {
    console.error('❌ 테스트 중 에러 발생:', err);
  } finally {
    await sequelize.close();
    console.log('🔚 DB 연결 종료');
  }
}

runReservationTests();
