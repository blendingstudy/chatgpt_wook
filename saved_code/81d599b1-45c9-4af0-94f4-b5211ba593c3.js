const express = require("express");
const app = express();
const port = 3000;

// 미들웨어 등록
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// 라우터 등록
const postRouter = require("./routes/post");
const userRouter = require("./routes/user");
const authRouter = require("./routes/auth");
app.use("/api/post", postRouter);
app.use("/api/user", userRouter);
app.use("/api/auth", authRouter);

// 서버 시작
app.listen(port, () => console.log(`Server started at http://localhost:${port}`));