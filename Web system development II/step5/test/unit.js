const assert = require('chai').assert;
const { User } = require('../models/');

describe('Simple Test', () => {
    before(() => {});
    after(() => {});
    beforeEach(() => {});
    afterEach(() => {});
    
    it('3 * 3 = 9', () => {
        assert.equal(3 * 3, 9);
    });
});

describe('ORM Test: [User Model]', () => {
    it('User.findOne(id=wkim)', async () => {
        const user = await User.findOne({
            where: { id: 'wkim' },
            attributes: ['id', 'name', 'description']
        });

        assert.equal('wkim', user.id);
    });
    
    it('User.findAll()', async () => {
        const users = await User.findAll({
            attributes: ['id', 'name', 'description']
        });

        assert.exists(users);
    });
});

