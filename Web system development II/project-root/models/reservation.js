// models/reservation.js
module.exports = (sequelize, DataTypes) => {
  const Reservation = sequelize.define('Reservation', {
    roomId: DataTypes.INTEGER,
    userId: DataTypes.INTEGER,
    purpose: DataTypes.STRING(100),
    startTime: DataTypes.DATE,
    endTime: DataTypes.DATE,
    status: {
      type: DataTypes.ENUM('pending', 'approved', 'rejected', 'canceled'),
      defaultValue: 'pending',
    },
  }, {
    tableName: 'reservations',
    timestamps: true,
  });

  return Reservation;
};
