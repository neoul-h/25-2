// routes/projects.js
const express = require('express');
const router = express.Router();
const projectController = require('../controllers/projectController');
const pool = require('../db');
const { authRequired } = require('../middlewares/auth');

// ✅ 프로젝트 멤버 여부 확인 미들웨어
async function requireProjectMember(req, res, next) {
  const projectId = req.params.id;
  const userId = req.user?.userId;

  if (!userId) return res.status(401).json({ message: '인증이 필요합니다.' });

  const conn = await pool.getConnection();
  try {
    const [rows] = await conn.query(
      'SELECT role FROM project_members WHERE project_id = ? AND user_id = ?',
      [projectId, userId]
    );
    if (rows.length === 0) {
      return res.status(403).json({ message: '프로젝트 접근 권한이 없습니다.' });
    }
    req.memberRole = rows[0].role; // owner/member
    next();
  } catch (err) {
    console.error('requireProjectMember error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  } finally {
    conn.release();
  }
}

// ✅ 프로젝트 오너(owner)만 허용
function requireProjectOwner(req, res, next) {
  if (req.memberRole !== 'owner') {
    return res.status(403).json({ message: '오너만 수행할 수 있습니다.' });
  }
  next();
}

// -------------------- 라우팅 --------------------

// 프로젝트 생성 (로그인 필요)
router.post('/', authRequired, projectController.createProject);

// 내 프로젝트 목록 (로그인 필요)  ← 전체 공개 목록 금지
router.get('/', authRequired, projectController.getProjects);

// 특정 프로젝트 상세 (멤버만)
router.get('/:id', authRequired, requireProjectMember, projectController.getProjectById);

// 프로젝트 수정 (오너만)
router.patch('/:id', authRequired, requireProjectMember, requireProjectOwner, projectController.updateProject);

// 프로젝트 삭제 (오너만)
router.delete('/:id', authRequired, requireProjectMember, requireProjectOwner, projectController.deleteProject);

// 프로젝트 멤버 추가 (오너만)
router.post('/:id/members', authRequired, requireProjectMember, requireProjectOwner, projectController.addMember);

// 프로젝트 멤버 목록 (멤버만)
router.get('/:id/members', authRequired, requireProjectMember, projectController.getMembers);

module.exports = router;

