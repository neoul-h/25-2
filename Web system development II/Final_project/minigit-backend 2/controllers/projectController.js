// controllers/projectController.js
// 프로젝트 관련 비즈니스 로직

const pool = require('../db');

// -------------------- helpers --------------------
function normalizeRole(role) {
  if (!role) return 'member';
  const r = String(role).toLowerCase();
  return (r === 'owner' || r === 'member') ? r : 'member';
}

// 프로젝트 생성
exports.createProject = async (req, res) => {
  try {
    const { name, description, due_at } = req.body;

    // ✅ owner는 토큰에서만
    const owner_id = req.user?.userId;

    if (!name || !owner_id) {
      return res.status(400).json({
        message: 'name은 필수이며, 로그인 상태여야 합니다.',
      });
    }

    const conn = await pool.getConnection();
    try {
      const [result] = await conn.query(
        'INSERT INTO projects (name, description, owner_id, due_at) VALUES (?, ?, ?, ?)',
        [name, description || null, owner_id, due_at || null]
      );

      const projectId = result.insertId;

      // project_members에 owner 추가
      await conn.query(
        'INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?)',
        [projectId, owner_id, 'owner']
      );

      res.status(201).json({
        message: '프로젝트 생성 성공',
        project: {
          id: projectId,
          name,
          description: description || null,
          owner_id,
          due_at: due_at || null,
        },
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('createProject error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 내 프로젝트 목록 조회
exports.getProjects = async (req, res) => {
  try {
    const userId = req.user?.userId;
    if (!userId) return res.status(401).json({ message: '인증이 필요합니다.' });

    const conn = await pool.getConnection();
    try {
      // ✅ "전체 프로젝트" 금지: 로그인한 사용자가 속한 프로젝트만
      const [rows] = await conn.query(
        `SELECT p.*
         FROM projects p
         JOIN project_members pm ON pm.project_id = p.id
         WHERE pm.user_id = ?
         ORDER BY p.created_at DESC`,
        [userId]
      );

      res.json({ projects: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getProjects error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 특정 프로젝트 상세 정보 (라우터에서 멤버검증 완료)
exports.getProjectById = async (req, res) => {
  try {
    const projectId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [projects] = await conn.query(
        'SELECT * FROM projects WHERE id = ?',
        [projectId]
      );

      if (projects.length === 0) {
        return res.status(404).json({ message: '프로젝트를 찾을 수 없습니다.' });
      }

      const project = projects[0];

      // 멤버 목록
      const [members] = await conn.query(
        `SELECT u.id, u.username, u.name, pm.role
         FROM project_members pm
         JOIN users u ON u.id = pm.user_id
         WHERE pm.project_id = ?
         ORDER BY (pm.role = 'owner') DESC, pm.created_at DESC`,
        [projectId]
      );

      // 문서 개수
      const [docs] = await conn.query(
        'SELECT COUNT(*) AS doc_count FROM documents WHERE project_id = ?',
        [projectId]
      );

      res.json({
        project,
        members,
        doc_count: docs[0].doc_count,
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getProjectById error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 프로젝트 수정 (라우터에서 owner 검증 완료)
exports.updateProject = async (req, res) => {
  try {
    const projectId = req.params.id;
    const { name, description, due_at } = req.body;

    const conn = await pool.getConnection();
    try {
      const [result] = await conn.query(
        `UPDATE projects
         SET name = COALESCE(?, name),
             description = COALESCE(?, description),
             due_at = COALESCE(?, due_at)
         WHERE id = ?`,
        [name || null, description || null, due_at || null, projectId]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '프로젝트를 찾을 수 없습니다.' });
      }

      const [rows] = await conn.query(
        'SELECT * FROM projects WHERE id = ?',
        [projectId]
      );

      res.json({
        message: '프로젝트 수정 성공',
        project: rows[0],
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('updateProject error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 프로젝트 삭제 (라우터에서 owner 검증 완료)
exports.deleteProject = async (req, res) => {
  try {
    const projectId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [result] = await conn.query(
        'DELETE FROM projects WHERE id = ?',
        [projectId]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '프로젝트를 찾을 수 없습니다.' });
      }

      res.json({ message: '프로젝트 삭제 성공' });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('deleteProject error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 프로젝트 멤버 추가 (username 기반)
// ✅ body: { username: "wlgjs07", role: "member" | "owner" }
exports.addMember = async (req, res) => {
  try {
    const projectId = req.params.id;
    const usernameRaw = req.body?.username;
    const role = normalizeRole(req.body?.role);

    const username = String(usernameRaw || '').trim();
    if (!username) {
      return res.status(400).json({ message: '아이디(username)는 필수입니다.' });
    }

    const conn = await pool.getConnection();
    try {
      // 1) username -> user_id 조회
      const [users] = await conn.query(
        'SELECT id FROM users WHERE username = ?',
        [username]
      );

      if (users.length === 0) {
        return res.status(404).json({
          message: `아이디 '${username}' 를 가진 사용자가 없습니다.`,
        });
      }

      const userId = users[0].id;

      // 2) 프로젝트 멤버로 추가
      await conn.query(
        'INSERT INTO project_members (project_id, user_id, role) VALUES (?, ?, ?)',
        [projectId, userId, role]
      );

      res.status(201).json({ message: '멤버 추가 성공' });
    } catch (err) {
      if (err.code === 'ER_DUP_ENTRY') {
        return res.status(409).json({ message: '이미 참여 중인 멤버입니다.' });
      }
      throw err;
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('addMember error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 프로젝트 멤버 목록 (라우터에서 member 검증 완료)
exports.getMembers = async (req, res) => {
  try {
    const projectId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [rows] = await conn.query(
        `SELECT u.id, u.username, u.name, pm.role, pm.created_at
         FROM project_members pm
         JOIN users u ON u.id = pm.user_id
         WHERE pm.project_id = ?
         ORDER BY (pm.role = 'owner') DESC, pm.created_at DESC`,
        [projectId]
      );

      res.json({ members: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getMembers error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};
