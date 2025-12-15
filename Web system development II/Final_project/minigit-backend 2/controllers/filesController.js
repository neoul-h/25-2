// controllers/filesController.js
const fs = require("fs");
const path = require("path");
const filesService = require("../services/fileService");

// RFC5987 파일명(한글/공백 안전)
function contentDispositionFilename(name) {
  const fallback = String(name || "file").replace(/["\\]/g, "_");
  const encoded = encodeURIComponent(name || "file");
  return `attachment; filename="${fallback}"; filename*=UTF-8''${encoded}`;
}

function contentDispositionInline(name) {
  const fallback = String(name || "file").replace(/["\\]/g, "_");
  const encoded = encodeURIComponent(name || "file");
  return `inline; filename="${fallback}"; filename*=UTF-8''${encoded}`;
}

// ✅ attachment 다운로드
exports.downloadVersionFile = async (req, res) => {
  try {
    const versionId = Number(req.params.versionId);
    const userId = req.user?.userId;

    if (!userId) return res.status(401).json({ message: "인증이 필요합니다." });
    if (!versionId || Number.isNaN(versionId)) {
      return res.status(400).json({ message: "versionId가 올바르지 않습니다." });
    }

    const auth = await filesService.getFileByVersionIdWithAuth(versionId, userId);
    if (!auth.ok) return res.status(auth.status).json({ message: auth.message });

    const meta = auth.data;
    const absPath = filesService.resolveUploadAbsPath(meta.file_path);

    // ✅ 파일 존재 확인
    if (!absPath || !fs.existsSync(absPath)) {
      return res.status(404).json({ message: "파일을 찾을 수 없습니다." });
    }

    res.setHeader("Content-Type", meta.file_type || "application/octet-stream");
    res.setHeader("Content-Disposition", contentDispositionFilename(meta.file_name || `version_${versionId}`));

    // res.download는 Content-Disposition을 다시 세팅할 수 있어서 sendFile로 통일
    return res.sendFile(absPath, (err) => {
      if (err && !res.headersSent) {
        return res.status(500).json({ message: "다운로드 실패", error: err.message });
      }
    });
  } catch (err) {
    return res.status(err.status || 500).json({ message: err.message || "서버 오류", error: err.message });
  }
};

// ✅ inline 미리보기
exports.inlineVersionFile = async (req, res) => {
  try {
    const versionId = Number(req.params.versionId);
    const userId = req.user?.userId;

    if (!userId) return res.status(401).json({ message: "인증이 필요합니다." });
    if (!versionId || Number.isNaN(versionId)) {
      return res.status(400).json({ message: "versionId가 올바르지 않습니다." });
    }

    const auth = await filesService.getFileByVersionIdWithAuth(versionId, userId);
    if (!auth.ok) return res.status(auth.status).json({ message: auth.message });

    const meta = auth.data;
    const absPath = filesService.resolveUploadAbsPath(meta.file_path);

    if (!absPath || !fs.existsSync(absPath)) {
      return res.status(404).json({ message: "파일을 찾을 수 없습니다." });
    }

    res.setHeader("Content-Type", meta.file_type || "application/octet-stream");
    res.setHeader("Content-Disposition", contentDispositionInline(meta.file_name || `version_${versionId}`));

    return res.sendFile(absPath, (err) => {
      if (err && !res.headersSent) {
        return res.status(500).json({ message: "미리보기 실패", error: err.message });
      }
    });
  } catch (err) {
    return res.status(err.status || 500).json({ message: err.message || "서버 오류", error: err.message });
  }
};
