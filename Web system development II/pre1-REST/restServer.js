const http = require('http');
const fs = require('fs').promises;

const URLS = { '/': './restFront.html', '/about': './about.html' };

const users = {};

http.createServer(async (req, res) => {
    const error = str => {
        res.writeHead(404);
        res.end(str || 'Page not found!');
    }

    const get = async () => {
        let data = '';

        try {
            if (req.url in URLS)
                data = await fs.readFile(URLS[req.url]);
            else
                switch (req.url) {
                    case '/users':
                        data = JSON.stringify(users);
                        break;
                    case '/favicon.ico':
                        res.end();
                        return;
                    default:
                        data = await fs.readFile(`.${req.url}`);
                        break;
                }

            res.writeHead(200);
            res.end(data);
        } catch (err) {
            error(err);
        }
    };

    const post = () => {
        switch (req.url) {
            case '/user':
                let body = '';
                req.on('data', data => body += data);
                req.on('end', () => {
                    console.log('POST-Body:', body);
                    const { name } = JSON.parse(body);
                    const id = Date.now();
                    users[id] = name;
                    res.writeHead(201);
                    res.end('OK');
                });

                break;

            default:
                error();
                break;
        }
    };

    const put = () => {
        if (req.url.startsWith('/user/')) {
            const key = req.url.split('/')[2];

            let body = '';
            req.on('data', data => body += data);
            req.on('end', () => {
                console.log('POST-Body:', body);
                users[key] = JSON.parse(body).name;
                res.writeHead(200);
                res.end('OK');
            });
        } else
            error();
    };

    const del = () => {
        if (req.url.startsWith('/user/')) {
            const key = req.url.split('/')[2];
            delete users[key];
            res.writeHead(200);
            res.end('ok');
        } else
            error();
    };

    const methods = { 'GET': get, 'POST': post, 'PUT': put, 'DELETE': del };
    methods[req.method]();
}).listen(8081, () => console.log('8081번 포트에서 서버 대기 중입니다'));
