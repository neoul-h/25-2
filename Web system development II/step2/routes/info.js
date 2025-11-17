const express = require('express');
const bcrypt = require('bcrypt');

const router = express.Router();


router.post('/message', (req, res) => {
    res.render("info", {
        title: 'Info-Message',
        message: req.body.msg
    });
});

router.get('/:id', (req, res) => {
    res.render("info", {
        title: 'Info-ID',
        message: req.params.id
    });
});

router.post('/password', async (req, res) => {
    global.password = await bcrypt.hash(req.body.password, 12);
    res.render("info", {
        title: 'Encrypted',
        message: global.password
    });
});

router.post('/compare', async (req, res) => {
    const auth = await bcrypt.compare(req.body.password, global.password);
    res.render("info", {
        title: 'Auth',
        message: auth
    });
});

module.exports = router;
