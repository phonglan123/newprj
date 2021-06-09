class Pefuha {
    // pefuha = PetaFunHash [^^]
    constructor(action, option) {
        this.versionSign = '@';
        switch (action) {
        	case 'test':
        		this.test();
            	break;
        	case 'setSign':
        		this.versionSign = option.versionSign;
            	break;
            default:
            	break;
        }
        /*
        	v1: !  v2: @  v3: #  v4: $  v5: %
            v6: ^  v7: &  v8: *  v9: ~  v10: =
            v11: +  v12: -  v13: _  v14: \  v15: |
            v16: ?  v17: /  v18: ;  v19: :  v20: P
        */
    }
    hash(string, hashLength = 4, randomEightNum = Math.floor(10000000 + Math.random() * 90000000), randomOneNum = Math.floor(Math.random() * 9) + 1) {
        var string = string.split(''),
            seed = randomEightNum.toString() + randomOneNum.toString() + hashLength.toString(),
            charset = 'abcdefghijklmnoqrstuvwxyzABCDEFGHIJKLMNOQRSTUVWXYZ';

        for (var i = 0; i < string.length; i++) {
            var temp = Math.pow((randomEightNum * Math.pow(string[i].charCodeAt(0), randomOneNum)), 1 / 4) * parseInt((randomOneNum * hashLength) / 10),
                result = parseInt(temp - parseInt(temp / Math.pow(10, hashLength)) * Math.pow(10, hashLength));
            string[i] = result;
            randomEightNum += randomOneNum;
        }
        
        string = string.join('').match(/.{1,2}/g);
        for (var i = 0; i < string.length; i++)
            string[i] = charset[(string[i] - 50 < 0) ? string[i] - 0 : string[i] - 50];

        return seed + this.versionSign + string.join('');
    }
    check(hashed, checkString) {
        var seed = hashed.split(this.versionSign)[0],
        	checked = this.hash(checkString, parseInt(seed.substring(9, seed.length)), parseInt(seed.substring(0, 8)), parseInt(seed.substring(8, 9)));
        return hashed == checked;
    }
    test() {
    	var testHashed = this.hash('chào');
    	console.log('%cvar hashed = new Pefuha().hash(\'chào\');', 'color: red');
    	console.log(testHashed);
    	console.log('%cvar checked = new Pefuha().check(hashed, \'cháo\');', 'color: red');
    	console.log('%c' + this.check(testHashed, 'cháo'), 'color: black');
	}
}
