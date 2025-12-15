// middlewares/auth.js
const jwt = require("jsonwebtoken");

function decodeToken(token) {
  const secret = process.env.JWT_SECRET;
  if (!secret) throw new Error("JWT_SECRET 누락");

  const decoded = jwt.verify(token, secret);

  // ✅ 호환: payload에 id만 있는 토큰도 userId로 매핑
  if (decoded && decoded.id && !decoded.userId) {
    decoded.userId = decoded.id;
  }

  return decoded;
}

// ✅ API(fetch)용: Authorization 헤더만 허용
function authRequired(req, res, next) {
  const h = req.headers.authorization;
  if (!h || !h.startsWith("Bearer ")) {
    return res.status(401).json({ message: "인증이 필요합니다." });
  }

  try {
    req.user = decodeToken(h.slice(7));
    next();
  } catch (e) {
    return res.status(401).json({ message: "토큰이 만료되었거나 유효하지 않습니다." });
  }
}

// ✅ 다운로드/iframe/img용: Authorization OR ?token= 허용
function authRequiredHeaderOrQuery(req, res, next) {
  try {
    const h = req.headers.authorization;

    let token = null;
    if (h && h.startsWith("Bearer ")) token = h.slice(7);
    else if (req.query?.token) token = String(req.query.token);

    if (!token) return res.status(401).json({ message: "인증이 필요합니다." });

    req.user = decodeToken(token);
    next();
  } catch (e) {
    return res.status(401).json({ message: "토큰이 만료되었거나 유효하지 않습니다." });
  }
}

module.exports = { authRequired, authRequiredHeaderOrQuery };
