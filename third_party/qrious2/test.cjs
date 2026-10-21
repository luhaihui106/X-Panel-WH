'use strict';
// Compare actual drawing operations: original minified fork, its unminified
// distribution source and our rebuilt minification. No panel/core is started.
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const assert = require('assert');
function load(file) {
    const operations = [];
    class Canvas {
        getContext() {
            return new Proxy({}, {
                set: (object, key, value) => {
                    operations.push([key, value]); object[key] = value; return true;
                },
                get: (object, key) => (...args) => operations.push([key, ...args])
            });
        }
        toDataURL(mime) { return 'data:' + mime; }
    }
    class Image {}
    const context = {
        document: {createElement: type => type === 'canvas' ? new Canvas() : new Image(),
            getElementById: () => null},
        HTMLCanvasElement: Canvas, HTMLImageElement: Image
    };
    vm.createContext(context);
    vm.runInContext(fs.readFileSync(file, 'utf8'), context);
    return {QRious: context.QRious, operations};
}
assert(process.env.QRIOUS_BUILD_OUTPUT, 'Set QRIOUS_BUILD_OUTPUT to the built scratch file');
const files = [path.join(__dirname, '../../web/assets/qrcode/qrious2.min.js'),
    path.join(__dirname, 'upstream/dist/qrious2.js'), process.env.QRIOUS_BUILD_OUTPUT];
const engines = files.map(load);
let cases = 0;
for (const value of ['', 'hello', '中文 العربية', 'vmess://' + 'a'.repeat(200), 'x'.repeat(1000)]) {
    for (const level of ['L', 'M', 'Q', 'H']) {
        for (const separator of ['D', 'E']) {
            const results = engines.map(engine => {
                engine.operations.length = 0;
                const qr = new engine.QRious({value, level, size: 257, padding: 3,
                    positionSep: separator, dataSep: separator, positionCorner: 4,
                    dataCornerTL: 2, dataCornerTR: 3, dataCornerBR: 4, dataCornerBL: 5});
                qr.set({value: value + 'changed', size: 311});
                qr.toDataURL();
                return JSON.stringify(engine.operations);
            });
            for (const result of results) assert.strictEqual(result, results[0]);
            cases++;
        }
    }
}
console.log(JSON.stringify({cases, passed: cases, files, scope: 'drawing operation equivalence, not a formal equivalence proof'}));
