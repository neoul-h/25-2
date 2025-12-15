// routes/versions.js
// 문서 버전(커밋) 생성/조회/삭제 + 권한 체크(프로젝트 멤버만)
// ✅ POST /versions : multer 파일 업로드 + task_id 필수 + document_versions insert + current_version 갱신

const express = require("express");
const router = express.Router();
const versionController = require("../controllers/versionController");
const pool = require("../db");
const { authRequired } = require("../middlewares/auth");

const multer = require("multer");
const path = require("path");
const fs = require("fs");

// -------------------- 업로드 설정 --------------------
const UPLOAD_DIR = path.join(__dirname, "..", "uploads");
const TMP_DIR = path.join(UPLOAD_DIR, "_tmp");

if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });
if (!fs.existsSync(TMP_DIR)) fs.mkdirSync(TMP_DIR, { recursive: true });

// 파일 저장 규칙 (최종): uploads/doc_<documentId>/<timestamp>_<safeName>
function ensureDocDir(documentId) {
  const dir = path.join(UPLOAD_DIR, `doc_${documentId}`);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function safeFilename(name) {
  return String(name || "file")
    .replace(/[^\w.\-가-힣 ]+/g, "_")
    .replace(/\s+/g, "_")
    .slice(0, 120);
}

// ✅ 우선 tmp에 저장(멀티파트에서 body/params 순서 이슈 방지)
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, TMP_DIR),
  filename: (req, file, cb) => cb(null, `${Date.now()}_${safeFilename(file.originalname)}`),
});

const upload = multer({
  storage,
  limits: { fileSize: 20 * 1024 * 1024 }, // 20MB
});

// -------------------- 권한 체크 --------------------

// ✅ documentId로 project_id를 찾아서 멤버인지 확인
async function requireProjectMemberByDocumentId(req, res, next) {
  const documentId = req.params.documentId || req.body.document_id;
  const userId = req.user?.userId;

  if (!userId) return res.status(401).json({ message: "인증이 필요합니다." });
  if (!documentId) return res.status(400).json({ message: "document_id가 필요합니다." });

  const conn = await pool.getConnection();
  try {
    const [docRows] = await conn.query("SELECT project_id FROM documents WHERE id = ?", [documentId]);
    if (docRows.length === 0) return res.status(404).json({ message: "문서를 찾을 수 없습니다." });

    const projectId = docRows[0].project_id;

    const [memRows] = await conn.query(
      "SELECT role FROM project_members WHERE project_id = ? AND user_id = ?",
      [projectId, userId]
    );
    if (memRows.length === 0) return res.status(403).json({ message: "프로젝트 접근 권한이 없습니다." });

    req.memberRole = memRows[0].role;
    req.projectId = projectId;
    req.documentId = Number(documentId);
    next();
  } catch (err) {
    console.error("requireProjectMemberByDocumentId error:", err);
    res.status(500).json({ message: "서버 오류", error: err.message });
  } finally {
    conn.release();
  }
}

// ✅ versionId로 document_id를 찾아서 (→ project_id) 멤버인지 확인
async function requireProjectMemberByVersionId(req, res, next) {
  const versionId = req.params.id;
  const userId = req.user?.userId;

  if (!userId) return res.status(401).json({ message: "인증이 필요합니다." });

  const conn = await pool.getConnection();
  try {
    const [verRows] = await conn.query("SELECT document_id FROM document_versions WHERE id = ?", [versionId]);
    if (verRows.length === 0) return res.status(404).json({ message: "버전을 찾을 수 없습니다." });

    const documentId = verRows[0].document_id;

    const [docRows] = await conn.query("SELECT project_id FROM documents WHERE id = ?", [documentId]);
    if (docRows.length === 0) return res.status(404).json({ message: "문서를 찾을 수 없습니다." });

    const projectId = docRows[0].project_id;

    const [memRows] = await conn.query(
      "SELECT role FROM project_members WHERE project_id = ? AND user_id = ?",
      [projectId, userId]
    );
    if (memRows.length === 0) return res.status(403).json({ message: "프로젝트 접근 권한이 없습니다." });

    req.memberRole = memRows[0].role;
    req.projectId = projectId;
    req.documentId = documentId;
    next();
  } catch (err) {
    console.error("requireProjectMemberByVersionId error:", err);
    res.status(500).json({ message: "서버 오류", error: err.message });
  } finally {
    conn.release();
  }
}

// -------------------- 라우팅 --------------------

// =====================================================
// ✅ 새 버전(커밋) 생성 (파일 업로드)
// POST /versions
// FormData fields:
// - document_id (필수)  <-- 프론트가 넣고 있음
// - task_id (필수)      <-- 요구사항: 강제
// - change_note (선택/권장)
// - content/learned/problem/todo (선택)
// - file (필수)
// =====================================================
router.post(
  "/",
  authRequired,
  upload.single("file"),
  requireProjectMemberByDocumentId,
  async (req, res) => {
    const authorId = req.user?.userId;

    // ✅ file 필수
    if (!req.file) return res.status(400).json({ message: "파일(file)은 필수입니다." });

    // ✅ document_id / task_id 필수
    const documentId = Number(req.body.document_id);
    const taskId = req.body.task_id ? Number(req.body.task_id) : null;

    if (!documentId || Number.isNaN(documentId)) {
      // tmp 파일 삭제
      try { fs.existsSync(req.file.path) && fs.unlinkSync(req.file.path); } catch {}
      return res.status(400).json({ message: "document_id는 필수입니다." });
    }
    if (!taskId || Number.isNaN(taskId)) {
      try { fs.existsSync(req.file.path) && fs.unlinkSync(req.file.path); } catch {}
      return res.status(400).json({ message: "task_id는 필수입니다." });
    }

    // 메타(선택)
    const change_note = (req.body.change_note || "").trim() || null;
    const content = (req.body.content || "").trim() || null;
    const learned = (req.body.learned || "").trim() || null;
    const problem = (req.body.problem || "").trim() || null;
    const todo = (req.body.todo || "").trim() || null;

    // 파일 메타
    const originalName = req.file.originalname;
    const mimeType = req.file.mimetype;
    const fileSize = req.file.size;

    // ✅ 최종 위치로 이동
    const docDir = ensureDocDir(documentId);
    const finalName = req.file.filename; // 이미 ts_safeName 형태
    const finalPathAbs = path.join(docDir, finalName);

    // 서버에서 접근 가능한 경로(정적서빙: /uploads)
    const relPath = `/uploads/doc_${documentId}/${finalName}`;

    const conn = await pool.getConnection();
    let moved = false;

    try {
      // tmp -> doc 폴더로 이동
      fs.renameSync(req.file.path, finalPathAbs);
      moved = true;

      await conn.beginTransaction();

      // 다음 버전 번호
      const [rows] = await conn.query(
        "SELECT COALESCE(MAX(version_no), 0) AS max_no FROM document_versions WHERE document_id = ?",
        [documentId]
      );
      const nextVersionNo = (rows[0]?.max_no || 0) + 1;

      // ✅ task_id가 실제로 이 프로젝트의 task인지(원하면 강제검증)
      // - 실수로 다른 프로젝트 task를 선택하는 걸 방지
      // - tasks 테이블이 project_id를 들고 있으니 확인 가능
      const [trows] = await conn.query("SELECT id FROM tasks WHERE id = ? AND project_id = ?", [
        taskId,
        req.projectId,
      ]);
      if (trows.length === 0) {
        throw new Error("선택한 task_id가 현재 프로젝트의 태스크가 아닙니다.");
      }

      // ✅ document_versions insert (파일 컬럼 포함)
      const [result] = await conn.query(
        `INSERT INTO document_versions
          (document_id, version_no, author_id, content, change_note, learned, problem, todo, task_id,
           file_name, file_path, file_type, file_size)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          documentId,
          nextVersionNo,
          authorId,
          content,
          change_note,
          learned,
          problem,
          todo,
          taskId,
          originalName,
          relPath,
          mimeType,
          fileSize,
        ]
      );

      const versionId = result.insertId;

      // 최신 버전 갱신
      await conn.query("UPDATE documents SET current_version_id = ? WHERE id = ?", [versionId, documentId]);

      await conn.commit();

      return res.status(201).json({
        message: "버전 업로드(커밋) 성공",
        version: {
          id: versionId,
          document_id: documentId,
          version_no: nextVersionNo,
          author_id: authorId,
          task_id: taskId,
          change_note,
          file_name: originalName,
          file_path: relPath,
          file_type: mimeType,
          file_size: fileSize,
          created_at: new Date().toISOString(),
        },
      });
    } catch (err) {
      try { await conn.rollback(); } catch {}
      console.error("create version(upload) error:", err);

      // 파일 정리: moved면 최종 파일 삭제, 아니면 tmp 삭제
      try {
        if (moved) {
          fs.existsSync(finalPathAbs) && fs.unlinkSync(finalPathAbs);
        } else {
          fs.existsSync(req.file.path) && fs.unlinkSync(req.file.path);
        }
      } catch {}

      return res.status(500).json({ message: "버전 업로드 처리 중 서버 오류", error: err.message });
    } finally {
      conn.release();
    }
  }
);

// ✅ 특정 문서의 전체 버전 조회
router.get(
  "/document/:documentId",
  authRequired,
  requireProjectMemberByDocumentId,
  versionController.getVersionsByDocument
);

// ✅ 버전을 문서의 최신 버전으로 적용
router.patch("/:id/apply", authRequired, requireProjectMemberByVersionId, versionController.applyVersion);

// ✅ 특정 버전 상세 조회
router.get("/:id", authRequired, requireProjectMemberByVersionId, versionController.getVersionById);

// ✅ 특정 버전 삭제
router.delete("/:id", authRequired, requireProjectMemberByVersionId, versionController.deleteVersion);

module.exports = router;
