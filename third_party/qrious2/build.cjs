'use strict';
// Offline after npm ci. Output stays outside runtime assets and the source tree.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const terser = require('terser');
const input = path.join(__dirname, 'upstream/dist/qrious2.js');
const expected = '528afc4d52510d19ac39fc957c94e8dc8c3e8aff3d8925e7c04133c9ae4ff219';
const source = fs.readFileSync(input);
if (crypto.createHash('sha256').update(source).digest('hex') !== expected) {
    throw new Error('Source changed: review provenance before building');
}
if (!process.env.QRIOUS_BUILD_OUTPUT || path.resolve(process.env.QRIOUS_BUILD_OUTPUT).startsWith(__dirname + path.sep)) {
    throw new Error('Set QRIOUS_BUILD_OUTPUT to a scratch file outside this source directory');
}
terser.minify(source.toString(), {format: {comments: /^!|Copyright|License|Permission|SOFTWARE/}}).then(result => {
    fs.writeFileSync(process.env.QRIOUS_BUILD_OUTPUT, result.code + '\n', {flag: 'wx'});
    console.log(JSON.stringify({output: process.env.QRIOUS_BUILD_OUTPUT,
        sha256: crypto.createHash('sha256').update(result.code + '\n').digest('hex'),
        exactHistoricalMinifierReproduction: false}));
}).catch(error => {console.error(error); process.exitCode = 1;});
