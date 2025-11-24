// models/room.js
module.exports = (sequelize, DataTypes) => {
  const Room = sequelize.define('Room', {
    floorId: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    name: {
      type: DataTypes.STRING(100),
      allowNull: false,
    },
    type: {
      type: DataTypes.ENUM('classroom', 'lab', 'hall', 'meeting', 'lounge', 'study', 'etc'),
      allowNull: false,
      defaultValue: 'etc',
    },
    capacity: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },
    isAvailable: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
      defaultValue: true,
    },
  }, {
    tableName: 'rooms',
    timestamps: true,
  });

  return Room;
};
