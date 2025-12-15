// controllers/taskController.js
// Task(TODO) 관리 로직

const pool = require('../db');

// 허용 status (원하는 값으로 조정 가능)
const ALLOWED_STATUS = new Set(['todo', 'doing', 'done']);

// username -> user_id 변환 + "프로젝트 멤버인지"까지 검증
async function resolveAssigneeId(conn, projectId, body) {
  // ✅ 프론트에서 이렇게 보내면 됨: { assignee_username: "wlgjs07" }
  const uname =
    (body.assignee_username ?? body.assigneeUsername ?? body.assigned_to_username ?? '').trim();

  // username을 안 보내면: (기존 방식) 숫자 id로도 호환
  if (!uname) {
    const id = body.assignee_id ?? body.assigned_to ?? null;
    return id ?? null;
  }

  // 1) username -> id 조회
  const [users] = await conn.query(
    'SELECT id FROM users WHERE username = ?',
    [uname]
  );

  if (users.length === 0) {
    const err = new Error(`아이디(username) '${uname}' 를 가진 사용자가 없습니다.`);
    err.status = 404;
    throw err;
  }

  const userId = users[0].id;

  // 2) 그 사람이 이 프로젝트 멤버인지 체크 (멤버 아니면 담당자 배정 불가)
  const [mem] = await conn.query(
    'SELECT 1 FROM project_members WHERE project_id = ? AND user_id = ?',
    [projectId, userId]
  );

  if (mem.length === 0) {
    const err = new Error(`'${uname}' 는 이 프로젝트 멤버가 아니어서 담당자로 지정할 수 없습니다.`);
    err.status = 400;
    throw err;
  }

  return userId;
}

// status 가드
function normalizeStatus(status) {
  const s = String(status ?? '').toLowerCase().trim();
  return ALLOWED_STATUS.has(s) ? s : null;
}

// -------------------- Task 생성 --------------------
exports.createTask = async (req, res) => {
  try {
    const { project_id, title, description, status } = req.body;

    if (!project_id || !title) {
      return res.status(400).json({
        message: 'project_id, title은 필수입니다.',
      });
    }

    const safeStatus = normalizeStatus(status) || 'todo';

    const conn = await pool.getConnection();
    try {
      // ✅ username 기반 담당자 처리 (없으면 id 방식도 호환)
      const assignee_id = await resolveAssigneeId(conn, project_id, req.body);

      const [result] = await conn.query(
        `INSERT INTO tasks
         (project_id, title, description, status, assignee_id)
         VALUES (?, ?, ?, ?, ?)`,
        [
          project_id,
          title,
          description || null,
          safeStatus,
          assignee_id || null,
        ]
      );

      // ✅ assignee의 name/username 같이 내려주기
      const [rows] = await conn.query(
        `SELECT t.*,
                u.name AS assignee_name,
                u.username AS assignee_username
         FROM tasks t
         LEFT JOIN users u ON u.id = t.assignee_id
         WHERE t.id = ?`,
        [result.insertId]
      );

      res.status(201).json({
        message: 'Task 생성 성공',
        task: rows[0],
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('createTask error:', err);
    res.status(err.status || 500).json({ message: err.message || '서버 오류', error: err.message });
  }
};

// -------------------- 프로젝트별 Task 목록 --------------------
exports.getTasksByProject = async (req, res) => {
  try {
    const projectId = req.params.projectId;
    const conn = await pool.getConnection();

    try {
      const [rows] = await conn.query(
        `SELECT t.*,
                u.name AS assignee_name,
                u.username AS assignee_username
         FROM tasks t
         LEFT JOIN users u ON u.id = t.assignee_id
         WHERE t.project_id = ?
         ORDER BY t.created_at DESC`,
        [projectId]
      );

      res.json({ tasks: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getTasksByProject error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// -------------------- Task 상세 --------------------
exports.getTaskById = async (req, res) => {
  try {
    const taskId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [rows] = await conn.query(
        `SELECT t.*,
                u.name AS assignee_name,
                u.username AS assignee_username
         FROM tasks t
         LEFT JOIN users u ON u.id = t.assignee_id
         WHERE t.id = ?`,
        [taskId]
      );

      if (rows.length === 0) {
        return res.status(404).json({ message: 'Task를 찾을 수 없습니다.' });
      }

      res.json({ task: rows[0] });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getTaskById error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// -------------------- Task 수정 --------------------
exports.updateTask = async (req, res) => {
  try {
    const taskId = req.params.id;
    const { title, description, status } = req.body;

    const conn = await pool.getConnection();
    try {
      // taskId로 project_id 가져오기 (담당자 username 검증하려고 필요)
      const [taskRows] = await conn.query('SELECT project_id FROM tasks WHERE id = ?', [taskId]);
      if (taskRows.length === 0) {
        return res.status(404).json({ message: 'Task를 찾을 수 없습니다.' });
      }
      const projectId = taskRows[0].project_id;

      // ✅ 동적 UPDATE: 들어온 것만 업데이트
      const fields = [];
      const params = [];

      if (title !== undefined) {
        fields.push('title = ?');
        params.push(title || null);
      }

      if (description !== undefined) {
        fields.push('description = ?');
        params.push(description || null);
      }

      if (status !== undefined) {
        const s = normalizeStatus(status);
        if (!s) return res.status(400).json({ message: "status는 'todo/doing/done' 중 하나여야 합니다." });
        fields.push('status = ?');
        params.push(s);
      }

      // ✅ 담당자: assignee_username 우선, 없으면 assignee_id/assigned_to 호환
      const hasAssigneeUsername =
        req.body.assignee_username !== undefined ||
        req.body.assigneeUsername !== undefined ||
        req.body.assigned_to_username !== undefined;

      const hasAssigneeId =
        req.body.assignee_id !== undefined || req.body.assigned_to !== undefined;

      if (hasAssigneeUsername || hasAssigneeId) {
        // 빈 문자열이면 "담당자 해제"로 처리
        const rawUname = (req.body.assignee_username ?? req.body.assigneeUsername ?? req.body.assigned_to_username ?? '');
        if (typeof rawUname === 'string' && rawUname.trim() === '') {
          fields.push('assignee_id = ?');
          params.push(null);
        } else {
          const assignee_id = await resolveAssigneeId(conn, projectId, req.body);
          fields.push('assignee_id = ?');
          params.push(assignee_id || null);
        }
      }

      if (fields.length === 0) {
        return res.status(400).json({ message: '수정할 값이 없습니다.' });
      }

      params.push(taskId);

      await conn.query(
        `UPDATE tasks SET ${fields.join(', ')} WHERE id = ?`,
        params
      );

      const [rows] = await conn.query(
        `SELECT t.*,
                u.name AS assignee_name,
                u.username AS assignee_username
         FROM tasks t
         LEFT JOIN users u ON u.id = t.assignee_id
         WHERE t.id = ?`,
        [taskId]
      );

      res.json({
        message: 'Task 수정 성공',
        task: rows[0],
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('updateTask error:', err);
    res.status(err.status || 500).json({ message: err.message || '서버 오류', error: err.message });
  }
};

// -------------------- Task 삭제 --------------------
exports.deleteTask = async (req, res) => {
  try {
    const taskId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [result] = await conn.query(
        'DELETE FROM tasks WHERE id = ?',
        [taskId]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: 'Task를 찾을 수 없습니다.' });
      }

      res.json({ message: 'Task 삭제 성공' });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('deleteTask error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};
