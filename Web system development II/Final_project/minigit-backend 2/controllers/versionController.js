// controllers/versionController.js
// 문서 버전(커밋) 관련 로직

const pool = require('../db');

// 새 버전 생성
exports.createVersion = async (req, res) => {
  try {
    const {
      document_id,
      content,
      change_note,
      learned,
      problem,
      todo,
      task_id,
      lines_added,
      lines_deleted,
    } = req.body;

    // ✅ author는 토큰에서만 (위조 방지)
    const author_id = req.user?.userId;

    if (!document_id || !author_id) {
      return res.status(400).json({
        message: 'document_id는 필수이며, 로그인 상태여야 합니다.',
      });
    }

    const conn = await pool.getConnection();
    try {
      // 현재 문서의 마지막 버전 번호 조회
      const [rows] = await conn.query(
        'SELECT COALESCE(MAX(version_no), 0) AS max_no FROM document_versions WHERE document_id = ?',
        [document_id]
      );
      const nextVersionNo = rows[0].max_no + 1;

      // 새 버전 insert
      const [result] = await conn.query(
        `INSERT INTO document_versions
         (document_id, version_no, author_id, content, change_note,
          learned, problem, todo, task_id, lines_added, lines_deleted)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          document_id,
          nextVersionNo,
          author_id,
          content || null,
          change_note || null,
          learned || null,
          problem || null,
          todo || null,
          task_id || null,
          lines_added || 0,
          lines_deleted || 0,
        ]
      );

      const versionId = result.insertId;

      // documents.current_version_id 갱신
      await conn.query(
        'UPDATE documents SET current_version_id = ? WHERE id = ?',
        [versionId, document_id]
      );

      res.status(201).json({
        message: '버전 생성 성공',
        version: {
          id: versionId,
          document_id,
          version_no: nextVersionNo,
          author_id,
        },
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('createVersion error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 특정 버전 상세
exports.getVersionById = async (req, res) => {
  try {
    const versionId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [rows] = await conn.query(
        'SELECT * FROM document_versions WHERE id = ?',
        [versionId]
      );

      if (rows.length === 0) {
        return res.status(404).json({ message: '버전을 찾을 수 없습니다.' });
      }

      res.json({ version: rows[0] });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getVersionById error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 특정 문서의 버전 목록
exports.getVersionsByDocument = async (req, res) => {
  try {
    const documentId = req.params.documentId;
    const conn = await pool.getConnection();

    try {
      const [rows] = await conn.query(
        `SELECT *
         FROM document_versions
         WHERE document_id = ?
         ORDER BY version_no ASC`,
        [documentId]
      );

      res.json({ versions: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getVersionsByDocument error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 버전 메타데이터 수정 (현재 라우트에 연결되어 있지 않지만 유지)
exports.updateVersion = async (req, res) => {
  try {
    const versionId = req.params.id;
    const {
      change_note,
      learned,
      problem,
      todo,
      task_id,
      lines_added,
      lines_deleted,
    } = req.body;

    const conn = await pool.getConnection();
    try {
      const [result] = await conn.query(
        `UPDATE document_versions
         SET change_note   = COALESCE(?, change_note),
             learned       = COALESCE(?, learned),
             problem       = COALESCE(?, problem),
             todo          = COALESCE(?, todo),
             task_id       = COALESCE(?, task_id),
             lines_added   = COALESCE(?, lines_added),
             lines_deleted = COALESCE(?, lines_deleted)
         WHERE id = ?`,
        [
          change_note || null,
          learned || null,
          problem || null,
          todo || null,
          task_id || null,
          lines_added ?? null,
          lines_deleted ?? null,
          versionId,
        ]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '버전을 찾을 수 없습니다.' });
      }

      const [rows] = await conn.query(
        'SELECT * FROM document_versions WHERE id = ?',
        [versionId]
      );

      res.json({
        message: '버전 수정 성공',
        version: rows[0],
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('updateVersion error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 버전 삭제
exports.deleteVersion = async (req, res) => {
  try {
    const versionId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [result] = await conn.query(
        'DELETE FROM document_versions WHERE id = ?',
        [versionId]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '버전을 찾을 수 없습니다.' });
      }

      res.json({ message: '버전 삭제 성공' });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('deleteVersion error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 버전을 문서의 최신 버전(current_version_id)에 반영
exports.applyVersion = async (req, res) => {
  try {
    const versionId = req.params.id;

    const conn = await pool.getConnection();

    try {
      // 해당 버전이 어떤 문서인지 조회
      const [rows] = await conn.query(
        'SELECT document_id FROM document_versions WHERE id = ?',
        [versionId]
      );

      if (rows.length === 0) {
        return res.status(404).json({ message: '버전을 찾을 수 없습니다.' });
      }

      const documentId = rows[0].document_id;

      // 문서 테이블의 current_version_id 갱신
      await conn.query(
        'UPDATE documents SET current_version_id = ? WHERE id = ?',
        [versionId, documentId]
      );

      res.json({
        message: '최신 버전으로 적용 완료',
        applied_version: versionId,
        document_id: documentId,
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('applyVersion error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};
