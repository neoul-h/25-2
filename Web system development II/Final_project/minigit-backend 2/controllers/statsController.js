// controllers/statsController.js
// 통계 / 기여도 분석용 쿼리 (✅ auth + 멤버 권한 체크 포함)

const pool = require("../db");

/**
 * ✅ 프로젝트 멤버 권한 체크
 * - req.user가 없으면(=authRequired 미들웨어 누락) 401
 * - 프로젝트 멤버가 아니면 403
 */
async function requireProjectMember(conn, projectId, userId) {
  if (!userId) {
    const err = new Error("인증이 필요합니다.");
    err.status = 401;
    throw err;
  }

  const [[row]] = await conn.query(
    `SELECT 1 AS ok
     FROM project_members
     WHERE project_id = ? AND user_id = ?
     LIMIT 1`,
    [projectId, userId]
  );

  if (!row) {
    const err = new Error("프로젝트에 대한 권한이 없습니다.");
    err.status = 403;
    throw err;
  }
}

// ---------------------- 멤버별 기여도 통계 ----------------------
exports.getContributions = async (req, res) => {
  const projectId = req.params.projectId;
  const userId = req.user?.id; // ✅ authRequired 전제

  let conn;
  try {
    conn = await pool.getConnection();

    // ✅ 멤버 권한 체크
    await requireProjectMember(conn, projectId, userId);

    const [rows] = await conn.query(
      `SELECT u.id AS user_id,
              u.name,
              COUNT(v.id) AS commit_count,
              COALESCE(SUM(v.lines_added), 0) AS lines_added,
              COALESCE(SUM(v.lines_deleted), 0) AS lines_deleted
       FROM project_members pm
       JOIN users u ON u.id = pm.user_id
       LEFT JOIN documents d ON d.project_id = pm.project_id
       LEFT JOIN document_versions v
              ON v.document_id = d.id
             AND v.author_id = u.id
       WHERE pm.project_id = ?
       GROUP BY u.id, u.name
       ORDER BY commit_count DESC`,
      [projectId]
    );

    res.json({ contributions: rows });
  } catch (err) {
    console.error("getContributions error:", err);
    res.status(err.status || 500).json({
      message: err.status ? err.message : "서버 오류",
      error: err.status ? undefined : err.message,
    });
  } finally {
    if (conn) conn.release();
  }
};

// ---------------------- Task 상태 통계 ----------------------
exports.getTaskStatusStats = async (req, res) => {
  const projectId = req.params.projectId;
  const userId = req.user?.id;

  let conn;
  try {
    conn = await pool.getConnection();

    // ✅ 멤버 권한 체크
    await requireProjectMember(conn, projectId, userId);

    const [rows] = await conn.query(
      `SELECT status, COUNT(*) AS count
       FROM tasks
       WHERE project_id = ?
       GROUP BY status`,
      [projectId]
    );

    res.json({ task_status_stats: rows });
  } catch (err) {
    console.error("getTaskStatusStats error:", err);
    res.status(err.status || 500).json({
      message: err.status ? err.message : "서버 오류",
      error: err.status ? undefined : err.message,
    });
  } finally {
    if (conn) conn.release();
  }
};

// ---------------------- 일자별 커밋 수 ----------------------
exports.getDailyCommits = async (req, res) => {
  const projectId = req.params.projectId;
  const userId = req.user?.id;

  let conn;
  try {
    conn = await pool.getConnection();

    // ✅ 멤버 권한 체크
    await requireProjectMember(conn, projectId, userId);

    const [rows] = await conn.query(
      `SELECT DATE(v.created_at) AS date,
              COUNT(v.id) AS commit_count
       FROM documents d
       JOIN document_versions v ON v.document_id = d.id
       WHERE d.project_id = ?
       GROUP BY DATE(v.created_at)
       ORDER BY date ASC`,
      [projectId]
    );

    res.json({ daily_commits: rows });
  } catch (err) {
    console.error("getDailyCommits error:", err);
    res.status(err.status || 500).json({
      message: err.status ? err.message : "서버 오류",
      error: err.status ? undefined : err.message,
    });
  } finally {
    if (conn) conn.release();
  }
};

// ---------------------- 프로젝트 전체 요약 ----------------------
exports.getProjectSummary = async (req, res) => {
  const projectId = req.params.projectId;
  const userId = req.user?.id;

  let conn;
  try {
    conn = await pool.getConnection();

    // ✅ 멤버 권한 체크
    await requireProjectMember(conn, projectId, userId);

    const [[project]] = await conn.query(
      `SELECT id, name, description, owner_id, created_at, updated_at
       FROM projects
       WHERE id = ?`,
      [projectId]
    );

    if (!project) {
      return res.status(404).json({ message: "프로젝트를 찾을 수 없습니다." });
    }

    const [[docCount]] = await conn.query(
      `SELECT COUNT(*) AS doc_count
       FROM documents
       WHERE project_id = ?`,
      [projectId]
    );

    const [[versionCount]] = await conn.query(
      `SELECT COUNT(*) AS version_count
       FROM documents d
       JOIN document_versions v ON v.document_id = d.id
       WHERE d.project_id = ?`,
      [projectId]
    );

    const [[memberCount]] = await conn.query(
      `SELECT COUNT(*) AS member_count
       FROM project_members
       WHERE project_id = ?`,
      [projectId]
    );

    res.json({
      project,
      summary: {
        documents: docCount.doc_count,
        versions: versionCount.version_count,
        members: memberCount.member_count,
      },
    });
  } catch (err) {
    console.error("getProjectSummary error:", err);
    res.status(err.status || 500).json({
      message: err.status ? err.message : "서버 오류",
      error: err.status ? undefined : err.message,
    });
  } finally {
    if (conn) conn.release();
  }
};

// ---------------------- 사용자 기준 참여 프로젝트 및 커밋 수 ----------------------
// 사용자 기준 참여 프로젝트 및 커밋 수
exports.getUserProjectStats = async (req, res) => {
  try {
    // ✅ 우선순위: 로그인 기반이면 req.user.id, 아니면 URL param
    const userId = req.user?.id || req.params.userId;

    if (!userId) {
      return res.status(400).json({ message: "userId가 필요합니다." });
    }

    const conn = await pool.getConnection();
    try {
      const [rows] = await conn.query(
        `SELECT p.id AS project_id,
                p.name AS project_name,
                COUNT(v.id) AS commit_count
         FROM project_members pm
         JOIN projects p ON p.id = pm.project_id
         LEFT JOIN documents d ON d.project_id = p.id
         LEFT JOIN document_versions v ON v.document_id = d.id
                                      AND v.author_id = pm.user_id
         WHERE pm.user_id = ?
         GROUP BY p.id, p.name
         ORDER BY p.created_at DESC`,
        [userId]
      );

      res.json({ projects: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error("getUserProjectStats error:", err);
    res.status(500).json({ message: "서버 오류", error: err.message });
  }
};
