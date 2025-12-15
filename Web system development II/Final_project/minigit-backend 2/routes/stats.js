// routes/stats.js
// 프로젝트 통계 / 기여도 분석

const express = require("express");
const router = express.Router();
const statsController = require("../controllers/statsController");

// 프로젝트 기여도 통계 (멤버별 커밋 수, 라인 수)
router.get("/project/:projectId/contributions", statsController.getContributions);

// 프로젝트 Task 상태 통계
router.get("/project/:projectId/tasks-status", statsController.getTaskStatusStats);

// 프로젝트 일자별 커밋 수
router.get("/project/:projectId/daily-commits", statsController.getDailyCommits);

// 프로젝트 전체 요약 (대시보드 느낌)
router.get("/project/:projectId/summary", statsController.getProjectSummary);

// ✅ 사용자 기준, 참여 프로젝트 + 커밋 수 (새 URL)
router.get("/user/projects", statsController.getUserProjectStats);

// ✅ (호환) 기존 URL도 유지
router.get("/user/:userId/projects", statsController.getUserProjectStats);

module.exports = router;
