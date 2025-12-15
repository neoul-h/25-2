// server.js
const express = require("express");
const dotenv = require("dotenv");
const path = require("path");

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// ❌ 업로드 정적서빙 제거 유지 OK
// app.use("/uploads", express.static(path.join(__dirname, "uploads")));

const authRouter = require("./routes/auth");
const projectsRouter = require("./routes/projects");
const documentsRouter = require("./routes/documents");
const versionsRouter = require("./routes/versions");
const statsRouter = require("./routes/stats");
const tasksRouter = require("./routes/tasks");
const filesRouter = require("./routes/files");

const { authRequired } = require("./middlewares/auth");

app.use("/auth", authRouter);

// ✅ 여기서 authRequired 걸지 마! (브라우저 링크는 헤더 못붙임)
app.use("/files", filesRouter);

app.use("/projects", authRequired, projectsRouter);
app.use("/documents", authRequired, documentsRouter);
app.use("/versions", authRequired, versionsRouter);
app.use("/tasks", authRequired, tasksRouter);
app.use("/stats", authRequired, statsRouter);

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// ✅ 테스트(supertest)에서 app만 import해서 쓸 수 있도록 export
module.exports = app;

// ✅ 직접 실행될 때만 listen (테스트에서는 listen 안 함)
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`🚀 MiniGit server running on port ${PORT}`);
  });
}
