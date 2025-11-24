// models/user.js
module.exports = (sequelize, DataTypes) => {
  const User = sequelize.define('User', {
    name: DataTypes.STRING(50),
    email: DataTypes.STRING(100),
    passwordHash: DataTypes.STRING(255),
    role: {
      type: DataTypes.ENUM('admin', 'manager', 'user'),
      defaultValue: 'user',
    },
  }, {
    tableName: 'users',
    timestamps: true,
  });

  return User;
};
