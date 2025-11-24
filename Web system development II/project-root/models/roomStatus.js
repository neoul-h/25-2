// models/roomStatus.js
module.exports = (sequelize, DataTypes) => {
  const RoomStatus = sequelize.define('RoomStatus', {
    roomId: DataTypes.INTEGER,
    temperature: DataTypes.FLOAT,
    humidity: DataTypes.FLOAT,
    occupancy: DataTypes.INTEGER,
    statusNote: DataTypes.STRING(100),
    measuredAt: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
    },
  }, {
    tableName: 'room_statuses',
    timestamps: true,
  });

  return RoomStatus;
};
