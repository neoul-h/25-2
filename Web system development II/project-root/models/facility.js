// models/facility.js
module.exports = (sequelize, DataTypes) => {
  const Facility = sequelize.define('Facility', {
    roomId: DataTypes.INTEGER,
    name: DataTypes.STRING(100),
    status: {
      type: DataTypes.ENUM('normal', 'broken', 'maintenance'),
      defaultValue: 'normal',
    },
    details: DataTypes.TEXT,
  }, {
    tableName: 'facilities',
    timestamps: true,
  });

  return Facility;
};
