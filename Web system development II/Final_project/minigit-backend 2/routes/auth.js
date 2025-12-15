// routes/auth.js
// 회원 관련 라우터 (회원가입 / 로그인 / 유저 목록)

const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// 회원가입
router.post('/register', authController.register);

// 로그인
router.post('/login', authController.login);

// 모든 사용자 목록 조회 (테스트용)  ← (보호는 app.js에서 처리)
router.get('/users', authController.getUsers);

module.exports = router;
