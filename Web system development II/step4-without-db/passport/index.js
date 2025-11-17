const passport = require('passport');
const local = require('./local');

module.exports = () => {
  passport.serializeUser((user, done) => {
    done(null, user.id);
  });

  passport.deserializeUser((id, done) => {
    done(null, global.users[id])
  });

  local();
};
