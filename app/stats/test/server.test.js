// server.test.js - unit tests for the ShopList stats service (lesson 8)
// Run: cd app/stats && npm test
// Uses only what comes with Node: node:test, node:http, fetch. No npm install.
// A tiny fake backend answers /products, so no real backend or database is needed.

const test = require('node:test');
const assert = require('node:assert');
const http = require('node:http');
const { spawn } = require('node:child_process');
const path = require('node:path');

const STATS_PORT = 3999;
const FAKE_BACKEND_PORT = 3998;

const PRODUCTS = [
  { name: 'Milk', price: 5, quantity: 3, category: 'Dairy', bought: false },
  { name: 'Bread', price: 10, quantity: 1, category: 'Bakery', bought: true }
];

let fakeBackend;
let stats;

test.before(async () => {
  // Fake backend: answers /products with the list above
  fakeBackend = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(PRODUCTS));
  });
  await new Promise(resolve => fakeBackend.listen(FAKE_BACKEND_PORT, resolve));

  // The real stats service, pointed at the fake backend
  stats = spawn(process.execPath, [path.join(__dirname, '..', 'server.js')], {
    env: { ...process.env, PORT: String(STATS_PORT), BACKEND_URL: `http://localhost:${FAKE_BACKEND_PORT}` }
  });
  // Wait until it prints "listening"
  await new Promise((resolve, reject) => {
    stats.stdout.on('data', data => { if (data.toString().includes('listening')) resolve(); });
    stats.on('exit', code => reject(new Error(`server.js exited with code ${code}`)));
  });
});

test.after(() => {
  stats.kill();
  fakeBackend.close();
});

test('GET /health returns ok', async () => {
  const res = await fetch(`http://localhost:${STATS_PORT}/health`);
  assert.strictEqual(res.status, 200);
  assert.deepStrictEqual(await res.json(), { status: 'ok' });
});

test('GET /stats calculates totals from the backend products', async () => {
  const res = await fetch(`http://localhost:${STATS_PORT}/stats`);
  assert.strictEqual(res.status, 200);
  const body = await res.json();
  assert.strictEqual(body.count, 2);
  assert.strictEqual(body.bought, 1);
  assert.strictEqual(body.total, 25);        // 5 x 3 + 10 x 1
  assert.strictEqual(body.leftToSpend, 15);  // only the milk is not bought
  assert.strictEqual(body.mostExpensive.name, 'Bread');
});

test('unknown route returns 404', async () => {
  const res = await fetch(`http://localhost:${STATS_PORT}/nope`);
  assert.strictEqual(res.status, 404);
});
