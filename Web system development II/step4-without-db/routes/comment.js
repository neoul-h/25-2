const express = require('express');

const { isLoggedIn } = require('./helpers');


const router = express.Router();

router.route('/')
    .get(isLoggedIn, (req, res) => {
        res.render('comment', {
            title: require('../package.json').name,
            userId: req.user.id
        });
    })
    .post(async (req, res, next) => {
        const { comment } = req.body;
        global.users[req.user.id].comments.push(comment);
        res.redirect('/');
    });

module.exports = router;
