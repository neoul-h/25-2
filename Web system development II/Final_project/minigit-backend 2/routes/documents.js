// routes/documents.js
// 문서 생성 / 조회 / 수정 / 삭제 / 프로젝트별 문서 조회 + 권한 체크 + ✅ 파일 업로드(커밋)

const express = require('express');
const router = express.Router();
const documentController = require('../controllers/documentController');
const pool = require('../db');
const { authRequired } = require('../middlewares/auth');

const multer = require('multer');
const path = require('path');
const fs = require('fs');

// -------------------- 업로드 설정 --------------------
const UPLOAD_DIR = path.join(__dirname, '..', 'uploads');

// uploads 폴더 없으면 생성
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// 파일 저장 규칙: uploads/doc_<documentId>/<timestamp>_<safeName>
function ensureDocDir(documentId) {
  const dir = path.join(UPLOAD_DIR, `doc_${documentId}`);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function safeFilename(name) {
  return String(name || 'file')
    .replace(/[^\w.\-가-힣 ]+/g, '_')
    .replace(/\s+/g, '_')
    .slice(0, 120);
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const documentId = req.params.id;
    const dir = ensureDocDir(documentId);
    cb(null, dir);
  },
  filename: (req, file, cb) => {
    const ts = Date.now();
    cb(null, `${ts}_${safeFilename(file.originalname)}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 20 * 1024 * 1024 } // 20MB (원하면 조절)
});

// -------------------- 권한 체크 --------------------

// ✅ projectId로 프로젝트 멤버인지 확인
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

    req.memberRole = rows[0].role;
    req.projectId = Number(projectId);
    next();
  } catch (err) {
    console.error('requireProjectMemberByProjectId error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  } finally {
    conn.release();
  }
}

// ✅ documentId로 문서의 project_id를 찾아서 그 프로젝트 멤버인지 확인
async function requireProjectMemberByDocumentId(req, res, next) {
  const documentId = req.params.id;
  const userId = req.user?.userId;

  if (!userId) return res.status(401).json({ message: '인증이 필요합니다.' });

  const conn = await pool.getConnection();
  try {
    const [docRows] = await conn.query(
      'SELECT project_id FROM documents WHERE id = ?',
      [documentId]
    );

    if (docRows.length === 0) {
      return res.status(404).json({ message: '문서를 찾을 수 없습니다.' });
    }

    const projectId = docRows[0].project_id;

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
    console.error('requireProjectMemberByDocumentId error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  } finally {
    conn.release();
  }
}

// -------------------- 라우팅 --------------------

// ✅ 특정 프로젝트의 문서 목록 (로그인 + 해당 프로젝트 멤버)
router.get(
  '/project/:projectId',
  authRequired,
  requireProjectMemberByProjectId,
  documentController.getDocumentsByProject
);

// ✅ 문서 생성 (로그인 + 해당 프로젝트 멤버)
router.post(
  '/',
  authRequired,
  requireProjectMemberByProjectId,
  documentController.createDocument
);

// ✅ 특정 문서 상세 (로그인 + 문서가 속한 프로젝트 멤버)
router.get(
  '/:id',
  authRequired,
  requireProjectMemberByDocumentId,
  documentController.getDocumentById
);

// ✅ 문서 수정 (로그인 + 문서가 속한 프로젝트 멤버)
router.patch(
  '/:id',
  authRequired,
  requireProjectMemberByDocumentId,
  documentController.updateDocument
);

// ✅ 문서 삭제 (로그인 + 문서가 속한 프로젝트 멤버)
router.delete(
  '/:id',
  authRequired,
  requireProjectMemberByDocumentId,
  documentController.deleteDocument
);

// =====================================================
// ✅ (핵심) 문서 파일 업로드 = git 커밋처럼
// POST /documents/:id/upload
// FormData fields:
// - file (필수)
// - task_id (선택)
// - change_note (필수처럼 쓰고 싶으면 프론트에서 강제)
// - learned/problem/todo (선택)
// 동작:
// 1) 파일 저장
// 2) document_versions insert (새 버전 생성)
// 3) documents.current_version_id = 새 버전
// 4) (선택) audit_log는 나중에 추가 가능
// =====================================================
router.post(
  '/:id/upload',
  authRequired,
  requireProjectMemberByDocumentId,
  upload.single('file'),
  async (req, res) => {
    const documentId = Number(req.params.id);
    const authorId = req.user?.userId;

    // 업로드 파일 필수
    if (!req.file) {
      return res.status(400).json({ message: '업로드할 파일(file)이 필요합니다.' });
    }

    // 메타/커밋 메시지
    const task_id = req.body.task_id ? Number(req.body.task_id) : null;
    const change_note = (req.body.change_note || '').trim() || null;
    const learned = (req.body.learned || '').trim() || null;
    const problem = (req.body.problem || '').trim() || null;
    const todo = (req.body.todo || '').trim() || null;

    // 파일 메타
    const originalName = req.file.originalname;
    const mimeType = req.file.mimetype;
    const fileSize = req.file.size;

    // 서버에서 접근 가능한 경로(정적서빙 기준)
    // 예: /uploads/doc_3/169..._report.pdf
    const relPath = `/uploads/doc_${documentId}/${req.file.filename}`;

    const conn = await pool.getConnection();
    try {
      await conn.beginTransaction();

      // 현재 문서의 마지막 버전 번호 조회
      const [rows] = await conn.query(
        'SELECT COALESCE(MAX(version_no), 0) AS max_no FROM document_versions WHERE document_id = ?',
        [documentId]
      );
      const nextVersionNo = rows[0].max_no + 1;

      // ✅ document_versions에 파일 정보까지 저장
      // ⚠️ 이 부분은 "DB에 컬럼 추가"가 필요함 (아래 안내 참고)
      const [result] = await conn.query(
        `INSERT INTO document_versions
          (document_id, version_no, author_id, change_note, learned, problem, todo, task_id,
           file_name, file_path, file_type, file_size)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          documentId,
          nextVersionNo,
          authorId,
          change_note,
          learned,
          problem,
          todo,
          task_id,
          originalName,
          relPath,
          mimeType,
          fileSize,
        ]
      );

      const versionId = result.insertId;

      // documents.current_version_id 갱신
      await conn.query(
        'UPDATE documents SET current_version_id = ? WHERE id = ?',
        [versionId, documentId]
      );

      await conn.commit();

      return res.status(201).json({
        message: '업로드(커밋) 성공: 새 버전이 생성되고 최신 버전으로 적용되었습니다.',
        version: {
          id: versionId,
          document_id: documentId,
          version_no: nextVersionNo,
          author_id: authorId,
          change_note,
          task_id,
          file: {
            name: originalName,
            path: relPath,
            type: mimeType,
            size: fileSize,
          }
        }
      });
    } catch (err) {
      await conn.rollback();

      console.error('upload commit error:', err);

      // 저장된 파일이 남으면 지움(트랜잭션 실패 시)
      try {
        if (req.file?.path && fs.existsSync(req.file.path)) fs.unlinkSync(req.file.path);
      } catch {}

      return res.status(500).json({ message: '업로드(커밋) 처리 중 서버 오류', error: err.message });
    } finally {
      conn.release();
    }
  }
);

module.exports = router;
