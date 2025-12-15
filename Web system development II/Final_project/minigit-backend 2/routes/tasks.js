// routes/tasks.js
// 프로젝트 Task(TODO) 관리 + 권한 체크(프로젝트 멤버만 접근)

const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');
const pool = require('../db');
const { authRequired } = require('../middlewares/auth');

// ✅ 특정 프로젝트의 멤버인지 확인
async function requireProjectMemberByProjectId(req, res, next) {
  const projectId = req.params.projectId || req.body.project_id;
  const userId = req.user?.userId;

  if (!userId) return res.status(401).json({ message: '인증이 필요합니다.' });
  if (!projectId) return res.status(400).json({ message: 'project_id가 필요합니다.' });

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
    req.projectId = Number(projectId);
    next();
  } catch (err) {
    console.error('requireProjectMemberByProjectId error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  } finally {
    conn.release();
  }
}

// ✅ taskId로 task의 project_id를 찾아서, 그 프로젝트 멤버인지 확인
async function requireProjectMemberByTaskId(req, res, next) {
  const taskId = req.params.id;
  const userId = req.user?.userId;

  if (!userId) return res.status(401).json({ message: '인증이 필요합니다.' });

  const conn = await pool.getConnection();
  try {
    const [taskRows] = await conn.query(
      'SELECT project_id FROM tasks WHERE id = ?',
      [taskId]
    );

    if (taskRows.length === 0) {
      return res.status(404).json({ message: 'Task를 찾을 수 없습니다.' });
    }

    const projectId = taskRows[0].project_id;

    const [memRows] = await conn.query(
      'SELECT role FROM project_members WHERE project_id = ? AND user_id = ?',
      [projectId, userId]
    );

    if (memRows.length === 0) {
      return res.status(403).json({ message: '프로젝트 접근 권한이 없습니다.' });
    }

    req.memberRole = memRows[0].role;
    req.projectId = projectId;
    next();
  } catch (err) {
    console.error('requireProjectMemberByTaskId error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  } finally {
    conn.release();
  }
}

// -------------------- 라우팅 --------------------

// Task 생성 (로그인 + 해당 프로젝트 멤버)
router.post('/', authRequired, requireProjectMemberByProjectId, taskController.createTask);

// 프로젝트별 Task 목록 (로그인 + 해당 프로젝트 멤버)
router.get(
  '/project/:projectId',
  authRequired,
  requireProjectMemberByProjectId,
  taskController.getTasksByProject
);

// Task 상세 (로그인 + Task가 속한 프로젝트 멤버)
router.get('/:id', authRequired, requireProjectMemberByTaskId, taskController.getTaskById);

// Task 수정 (로그인 + Task가 속한 프로젝트 멤버)
router.patch('/:id', authRequired, requireProjectMemberByTaskId, taskController.updateTask);

// Task 삭제 (로그인 + Task가 속한 프로젝트 멤버)
router.delete('/:id', authRequired, requireProjectMemberByTaskId, taskController.deleteTask);

module.exports = router;
