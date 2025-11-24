// models/malfunction.js
module.exports = (sequelize, DataTypes) => {
  const Malfunction = sequelize.define('Malfunction', {
    roomId: DataTypes.INTEGER,
    facilityId: DataTypes.INTEGER,
    reportedBy: DataTypes.INTEGER,
    description: DataTypes.TEXT,
    severity: {
      type: DataTypes.ENUM('low', 'medium', 'high'),
      defaultValue: 'low',
    },
    status: {
      type: DataTypes.ENUM('open', 'in_progress', 'resolved'),
      defaultValue: 'open',
    },
    reportedAt: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
    },
    resolvedAt: {
      type: DataTypes.DATE,
      allowNull: true,
    },
  }, {
    tableName: 'malfunctions',
    timestamps: true,
  });

  return Malfunction;
};
