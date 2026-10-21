'use strict';
// Offline after npm ci. Output stays outside runtime assets and the source tree.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const terser = require('terser');
// This readable fork is our preferred editable source. Historical upstream
// materials remain untouched for provenance, not as hidden build inputs.
const input = path.join(__dirname, 'src/qrious2.js');
const source = fs.readFileSync(input);
if (!process.env.QRIOUS_BUILD_OUTPUT || path.resolve(process.env.QRIOUS_BUILD_OUTPUT).startsWith(__dirname + path.sep)) {
    throw new Error('Set QRIOUS_BUILD_OUTPUT to a scratch file outside this source directory');
}
terser.minify(source.toString(), {format: {comments: /^!|Copyright|License|Permission|SOFTWARE/}}).then(result => {
    fs.writeFileSync(process.env.QRIOUS_BUILD_OUTPUT, result.code + '\n', {flag: 'wx'});
    console.log(JSON.stringify({output: process.env.QRIOUS_BUILD_OUTPUT,
        input, inputSha256: crypto.createHash('sha256').update(source).digest('hex'),
        sha256: crypto.createHash('sha256').update(result.code + '\n').digest('hex'),
        exactHistoricalMinifierReproduction: false}));
}).catch(error => {console.error(error); process.exitCode = 1;});
