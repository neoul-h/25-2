// app.js
require('dotenv').config();
const express = require('express');
const { sequelize } = require('./models');

const buildingRouter = require('./routes/buildingRouter');
const floorRouter = require('./routes/floorRouter');
const roomRouter = require('./routes/roomRouter');
const reservationRouter = require('./routes/reservationRouter');
const malfunctionRouter = require('./routes/malfunctionRouter');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());

app.use('/buildings', buildingRouter);
app.use('/floors', floorRouter);
app.use('/rooms', roomRouter);
app.use('/reservations', reservationRouter);
app.use('/malfunctions', malfunctionRouter);

app.get('/', (req, res) => {
  res.json({ success: true, message: 'Digital Twin Campus API Server' });
});

sequelize.sync({ alter: false })
  .then(() => {
    console.log('✅ DB 연결 및 모델 동기화 성공');
    app.listen(PORT, () => {
      console.log(`✅ 서버 실행 중: http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('❌ DB 연결 실패:', err);
  });
