// Renders docs/architektura.svg to docs/architektura.png (2x). Needs: npm i playwright
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const docs = path.resolve(__dirname, '..', 'docs');
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 680, height: 666 } });
  await p.goto('file://' + path.join(docs, 'architektura.svg'));
  await p.screenshot({ path: path.join(docs, 'architektura.png'), clip: { x: 0, y: 0, width: 680, height: 666 } });
  await b.close();
})();
