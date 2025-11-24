// models/building.js
module.exports = (sequelize, DataTypes) => {
  const Building = sequelize.define('Building', {
    name: {
      type: DataTypes.STRING(100),
      allowNull: false,
    },
    code: {
      type: DataTypes.STRING(20),
      allowNull: true,
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true,
    },
  }, {
    tableName: 'buildings',
    timestamps: true,
  });

  return Building;
};
