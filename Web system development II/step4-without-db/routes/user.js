const express = require('express');
const bcrypt = require('bcrypt')

const { logout } = require('./helpers');


const router = express.Router();

router.route('/')
    .get((req, res) => {
        console.log(Object.keys(global.users))
        res.render('user', {
        title: require('../package.json').name,
        port: process.env.PORT,
        users: Object.keys(global.users)
    })})
    .post(async (req, res, next) => {
        const { id, password, name, description } = req.body;

        if (id in global.users) {
            next('이미 등록된 사용자 아이디입니다.');
            return;
        }

        global.users[id] = {
            id,
            password: await bcrypt.hash(password, 12),
            name,
            description,
            comments: []
        };

        res.redirect('/');
    });

router.post('/update', (req, res, next) => {
    const { id, description } = req.body;

    if (id in global.users) {
        global.users[id].description = description;
        res.redirect('/');
    } else
        next(`There is no user with ${req.params.id}.`);
});

router.get('/delete/:id', (req, res, next) => {
    if (req.params.id in global.users) {
        delete global.users[req.params.id];
        next();
    } else
        next(`There is no user with ${req.params.id}.`);
}, logout);

router.get('/:id/comments', (req, res, next) => {
    if (req.params.id in global.users)
        res.json(global.users[req.params.id].comments);
    else
        next(`There is no user with ${req.params.id}.`);
});

router.get('/:id', (req, res, next) => {
    if (req.params.id in global.users)
        res.json(global.users[req.params.id]);
    else
        next(`There is no user with ${req.params.id}.`);
});

module.exports = router;
