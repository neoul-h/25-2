// controllers/documentController.js
// 문서 CRUD 로직

const pool = require('../db');

// 문서 생성
exports.createDocument = async (req, res) => {
  try {
    const { project_id, title, description } = req.body;

    // ✅ owner는 토큰에서만 (위조 방지)
    const owner_id = req.user?.userId;

    if (!project_id || !title || !owner_id) {
      return res.status(400).json({
        message: 'project_id, title은 필수이며, 로그인 상태여야 합니다.',
      });
    }

    const conn = await pool.getConnection();
    try {
      const [result] = await conn.query(
        'INSERT INTO documents (project_id, title, description, owner_id) VALUES (?, ?, ?, ?)',
        [project_id, title, description || null, owner_id]
      );

      res.status(201).json({
        message: '문서 생성 성공',
        document: {
          id: result.insertId,
          project_id,
          title,
          description: description || null,
          owner_id,
        },
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('createDocument error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 특정 문서 상세
exports.getDocumentById = async (req, res) => {
  try {
    const documentId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [docs] = await conn.query(
        'SELECT * FROM documents WHERE id = ?',
        [documentId]
      );

      if (docs.length === 0) {
        return res.status(404).json({ message: '문서를 찾을 수 없습니다.' });
      }

      const document = docs[0];

      // 해당 문서의 버전 목록도 같이 내려줄 수 있음
      const [versions] = await conn.query(
        `SELECT id, version_no, author_id, change_note, created_at
         FROM document_versions
         WHERE document_id = ?
         ORDER BY version_no ASC`,
        [documentId]
      );

      res.json({
        document,
        versions,
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getDocumentById error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 문서 수정
exports.updateDocument = async (req, res) => {
  try {
    const documentId = req.params.id;
    const { title, description } = req.body;

    const conn = await pool.getConnection();
    try {
      const [result] = await conn.query(
        `UPDATE documents
         SET title = COALESCE(?, title),
             description = COALESCE(?, description)
         WHERE id = ?`,
        [title || null, description || null, documentId]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '문서를 찾을 수 없습니다.' });
      }

      const [rows] = await conn.query(
        'SELECT * FROM documents WHERE id = ?',
        [documentId]
      );

      res.json({
        message: '문서 수정 성공',
        document: rows[0],
      });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('updateDocument error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 문서 삭제
exports.deleteDocument = async (req, res) => {
  try {
    const documentId = req.params.id;
    const conn = await pool.getConnection();

    try {
      const [result] = await conn.query(
        'DELETE FROM documents WHERE id = ?',
        [documentId]
      );

      if (result.affectedRows === 0) {
        return res.status(404).json({ message: '문서를 찾을 수 없습니다.' });
      }

      res.json({ message: '문서 삭제 성공' });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('deleteDocument error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};

// 특정 프로젝트의 문서 목록
exports.getDocumentsByProject = async (req, res) => {
  try {
    const projectId = req.params.projectId;
    const conn = await pool.getConnection();

    try {
      const [rows] = await conn.query(
        'SELECT * FROM documents WHERE project_id = ? ORDER BY created_at DESC',
        [projectId]
      );

      res.json({ documents: rows });
    } finally {
      conn.release();
    }
  } catch (err) {
    console.error('getDocumentsByProject error:', err);
    res.status(500).json({ message: '서버 오류', error: err.message });
  }
};
