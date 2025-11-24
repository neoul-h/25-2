// models/floor.js
module.exports = (sequelize, DataTypes) => {
  const Floor = sequelize.define('Floor', {
    buildingId: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    floorNumber: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
    name: {
      type: DataTypes.STRING(50),
      allowNull: false,
    },
  }, {
    tableName: 'floors',
    timestamps: true,
  });

  return Floor;
};
