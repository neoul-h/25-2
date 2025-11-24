const request = require("supertest");
const app = require("../app");

describe('API Test: [User]', () => {
    it('GET /users', done => {
        request(app)
            .get("/users")
            .expect(res => {
                console.log(res.body);
            })
            .expect(200, done);
    });

    it('GET /user/wkim', done => {
        request(app)
            .get("/user/wkim")
            .expect(res => {
                console.log(res.body);
            })
            .expect(200, { 
                id: 'wkim', name: '김원빈', description: '' 
            }, done);
    });

    // npx mocha --exit -f POST test/api.js
    // -f: 지정한 문자열을 포함하는 테스트만 진행
    it('POST /user/update', done => {
        request(app)
            .post("/user/update")
            .send({ id: "wkim", description: "" })
            .expect(302, done);
    });
});
