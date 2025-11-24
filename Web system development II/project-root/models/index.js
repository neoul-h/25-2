// models/index.js
const { Sequelize, DataTypes } = require('sequelize');
const config = require('../config/config');

const sequelize = new Sequelize(
  config.database,
  config.username,
  config.password,
  {
    host: config.host,
    dialect: config.dialect,
    logging: config.logging,
  }
);

// 모델 정의
const User = require('./user')(sequelize, DataTypes);
const Building = require('./building')(sequelize, DataTypes);
const Floor = require('./floor')(sequelize, DataTypes);
const Room = require('./room')(sequelize, DataTypes);
const Facility = require('./facility')(sequelize, DataTypes);
const RoomStatus = require('./roomStatus')(sequelize, DataTypes);
const Reservation = require('./reservation')(sequelize, DataTypes);
const Malfunction = require('./malfunction')(sequelize, DataTypes);

// 관계 설정
Building.hasMany(Floor, { foreignKey: 'buildingId' });
Floor.belongsTo(Building, { foreignKey: 'buildingId' });

Floor.hasMany(Room, { foreignKey: 'floorId' });
Room.belongsTo(Floor, { foreignKey: 'floorId' });

Room.hasMany(Facility, { foreignKey: 'roomId' });
Facility.belongsTo(Room, { foreignKey: 'roomId' });

Room.hasMany(RoomStatus, { foreignKey: 'roomId' });
RoomStatus.belongsTo(Room, { foreignKey: 'roomId' });

Room.hasMany(Reservation, { foreignKey: 'roomId' });
Reservation.belongsTo(Room, { foreignKey: 'roomId' });

User.hasMany(Reservation, { foreignKey: 'userId' });
Reservation.belongsTo(User, { foreignKey: 'userId' });

Room.hasMany(Malfunction, { foreignKey: 'roomId' });
Malfunction.belongsTo(Room, { foreignKey: 'roomId' });

Facility.hasMany(Malfunction, { foreignKey: 'facilityId' });
Malfunction.belongsTo(Facility, { foreignKey: 'facilityId' });

User.hasMany(Malfunction, { foreignKey: 'reportedBy' });
Malfunction.belongsTo(User, { foreignKey: 'reportedBy' });

module.exports = {
  sequelize,
  User,
  Building,
  Floor,
  Room,
  Facility,
  RoomStatus,
  Reservation,
  Malfunction,
};
