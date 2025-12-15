// routes/files.js
const express = require("express");
const router = express.Router();
const filesController = require("../controllers/filesController");
const { authRequiredHeaderOrQuery } = require("../middlewares/auth");

// ✅ 다운로드(attachment)
router.get("/version/:versionId", authRequiredHeaderOrQuery, filesController.downloadVersionFile);

// ✅ 미리보기(inline)
router.get("/version/:versionId/inline", authRequiredHeaderOrQuery, filesController.inlineVersionFile);

module.exports = router;
