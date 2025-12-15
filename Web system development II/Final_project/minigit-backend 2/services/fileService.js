// services/fileService.js
const pool = require("../db");
const path = require("path");
const fs = require("fs");

// versionId 기준: 프로젝트 멤버 권한 + 파일 메타 가져오기
async function getFileByVersionIdWithAuth(versionId, userId) {
  const conn = await pool.getConnection();
  try {
    const [rows] = await conn.query(
      `
      SELECT
        dv.id AS version_id,
        dv.document_id,
        d.project_id,
        pm.role AS member_role,
        dv.file_name,
        dv.file_path,
        dv.file_type,
        dv.file_size
      FROM document_versions dv
      JOIN documents d ON d.id = dv.document_id
      LEFT JOIN project_members pm
        ON pm.project_id = d.project_id
       AND pm.user_id = ?
      WHERE dv.id = ?
      LIMIT 1
      `,
      [userId, versionId]
    );

    if (rows.length === 0) return { ok: false, status: 404, message: "버전을 찾을 수 없습니다." };

    const r = rows[0];
    if (!r.member_role) return { ok: false, status: 403, message: "프로젝트 접근 권한이 없습니다." };
    if (!r.file_path) return { ok: false, status: 404, message: "이 버전에는 업로드 파일이 없습니다." };

    return { ok: true, data: r };
  } finally {
    conn.release();
  }
}

// DB의 file_path(/uploads/...) -> 실제 uploads 폴더 abs 경로로 변환 + 탈출 방지
function resolveUploadAbsPath(filePathFromDb) {
  const UPLOAD_ROOT = path.resolve(__dirname, "..", "uploads"); // 절대경로 고정

  // "/uploads/doc_3/xxx.pdf" -> "doc_3/xxx.pdf"
  const rel = String(filePathFromDb || "")
    .replace(/^\/uploads\/?/, "")
    .replace(/^uploads\/?/, "");

  // ✅ resolve로 정규화 + 루트 밖으로 못 나가게
  const abs = path.resolve(UPLOAD_ROOT, rel);

  // UPLOAD_ROOT 하위인지 검사 (경로 탈출 방지)
  const rootPrefix = UPLOAD_ROOT.endsWith(path.sep) ? UPLOAD_ROOT : UPLOAD_ROOT + path.sep;
  if (!(abs + path.sep).startsWith(rootPrefix)) {
    const err = new Error("잘못된 파일 경로입니다.");
    err.status = 400;
    throw err;
  }

  if (!fs.existsSync(abs)) {
    const err = new Error("파일이 서버에 존재하지 않습니다.");
    err.status = 404;
    throw err;
  }

  return abs;
}

module.exports = { getFileByVersionIdWithAuth, resolveUploadAbsPath };
