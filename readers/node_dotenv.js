// readers/node_dotenv.js
const fs = require("fs");
const dotenv = require("dotenv");
const { expand } = require("dotenv-expand");

const plain = dotenv.parse(fs.readFileSync(process.argv[2]));
const expanded = expand({ parsed: { ...plain }, processEnv: {} }).parsed;
console.log(JSON.stringify({ plain, expanded }));
